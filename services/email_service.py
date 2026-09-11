# services/email_service.py
"""
Serviço de envio de email de notificação de novo chamado no GLPI.
Layout baseado no modelo de referência (header escuro, ícones de
Requerente/Status/Atribuído, caixa com os dados do formulário e botão
de acesso ao chamado).
"""

import re
import html as html_lib
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from email.utils import formataddr
import mimetypes  # ADICIONADO: para detectar tipo MIME

from config import settings, logger

# Tags que vamos MANTER no conteúdo do formulário — simples o suficiente
# pra qualquer cliente de email (inclusive Outlook desktop) renderizar sem
# quebrar. Tudo que não estiver aqui é removido.
_ALLOWED_TAGS_RE = re.compile(r'</?(b|strong|br|i|em|u|a)\b[^>]*>', re.IGNORECASE)
_ANY_TAG_RE = re.compile(r'<[^>]+>')
_A_WRAPPING_IMG_RE = re.compile(
    r'<a\b[^>]*\bhref=["\']([^"\']+)["\'][^>]*>\s*<img[^>]*>\s*</a>',
    re.IGNORECASE | re.DOTALL,
)
_BARE_IMG_SRC_RE = re.compile(r'<img[^>]*\bsrc=["\']([^"\']+)["\'][^>]*>', re.IGNORECASE)
_IMG_TAG_RE = re.compile(r'<img[^>]*>', re.IGNORECASE)  # sobra sem src, se houver
_HEADER_RE = re.compile(r'<h[1-4][^>]*>(.*?)</h[1-4]>', re.IGNORECASE | re.DOTALL)
_A_OPEN_RE = re.compile(r'<a\b[^>]*>', re.IGNORECASE)
_A_CLOSE_RE = re.compile(r'</a>', re.IGNORECASE)
_DIV_OPEN_RE = re.compile(r'<div[^>]*>', re.IGNORECASE)
_DIV_CLOSE_RE = re.compile(r'</div>', re.IGNORECASE)
_P_OPEN_RE = re.compile(r'<p[^>]*>', re.IGNORECASE)
_P_CLOSE_RE = re.compile(r'</p>', re.IGNORECASE)
_MULTI_BR_RE = re.compile(r'(<br\s*/?>\s*){2,}', re.IGNORECASE)


def _glpi_domain() -> str:
    """Extrai só o domínio (esquema+host+porta) a partir do GLPI_TICKET_BASE_URL."""
    base = settings.GLPI_TICKET_BASE_URL
    idx = base.find('/front/')
    return base[:idx] if idx != -1 else base.rstrip('/')


def _to_absolute_glpi_url(path: str) -> str:
    """Transforma um caminho relativo do GLPI (ex: /front/document.send.php?...) numa URL completa e clicável."""
    if path.startswith('http://') or path.startswith('https://'):
        return path
    if not path.startswith('/'):
        path = '/' + path
    return _glpi_domain() + path


def simplify_form_content(raw_html: str) -> str:
    """
    Converte o HTML rico que o GLPI/Formcreator gera (divs aninhadas,
    h1/h2, links com imagem embutida, URLs relativas, etc.) num HTML
    minimalista — evita que clientes de email (Outlook em especial)
    quebrem o parsing, e transforma imagens/anexos em links absolutos
    clicáveis (URL relativa não funciona fora do GLPI).
    """
    if not raw_html:
        return ""

    text = raw_html

    # Placeholders temporários pros links de imagem — protegidos de qualquer
    # remoção de tag que rola mais adiante, e restaurados só no final.
    _tokens: list[str] = []

    def _store_image_link(href: str) -> str:
        abs_url = _to_absolute_glpi_url(href)
        token = f"@@IMGLINK{len(_tokens)}@@"
        _tokens.append(f'<a href="{abs_url}" target="_blank">📎 Ver imagem/anexo</a>')
        return token

    # <a href="...">...<img .../>...</a>  -> vira link absoluto com o próprio href
    text = _A_WRAPPING_IMG_RE.sub(lambda m: _store_image_link(m.group(1)), text)

    # <img src="..."> solto (sem <a> em volta) -> vira link absoluto com o src
    text = _BARE_IMG_SRC_RE.sub(lambda m: _store_image_link(m.group(1)), text)

    # Qualquer <img> residual sem src identificável — remove sem deixar rastro
    text = _IMG_TAG_RE.sub('', text)

    # Remove <a> e </a> restantes (links comuns, não-imagem) mas mantém o texto
    text = _A_OPEN_RE.sub('', text)
    text = _A_CLOSE_RE.sub('', text)

    # Cabeçalhos (h1/h2/h3/h4) viram uma linha em negrito
    text = _HEADER_RE.sub(r'<br><b>\1</b><br>', text)

    # div/p viram quebra de linha ao fechar
    text = _DIV_OPEN_RE.sub('', text)
    text = _DIV_CLOSE_RE.sub('<br>', text)
    text = _P_OPEN_RE.sub('', text)
    text = _P_CLOSE_RE.sub('<br>', text)

    # Remove qualquer outra tag que não seja b/strong/br/i/em/u (os links de
    # imagem já viraram token de texto puro, então não são afetados aqui)
    text = _ANY_TAG_RE.sub(lambda m: m.group(0) if _ALLOWED_TAGS_RE.fullmatch(m.group(0)) else '', text)

    # Decodifica entidades HTML (&aacute; -> á, &amp; -> & etc.)
    text = html_lib.unescape(text)

    # Colapsa <br> repetidos em um só, e tira espaços nas pontas
    text = _MULTI_BR_RE.sub('<br>', text)
    text = text.strip()
    while text.startswith('<br>'):
        text = text[4:].strip()
    while text.endswith('<br>'):
        text = text[:-4].strip()

    # Restaura os links de imagem no lugar dos tokens
    for i, snippet in enumerate(_tokens):
        text = text.replace(f"@@IMGLINK{i}@@", snippet)

    return text


class EmailService:
    def __init__(self):
        self.host = settings.SMTP_HOST
        self.port = settings.SMTP_PORT
        self.user = settings.SMTP_USER
        self.password = settings.SMTP_PASSWORD
        self.from_name = settings.SMTP_FROM_NAME
        self.from_email = settings.SMTP_FROM_EMAIL
        self.recipients = settings.NOTIFICATION_RECIPIENTS
        self.notify_cc_requester = settings.NOTIFY_CC_REQUESTER
        self.ticket_base_url = settings.GLPI_TICKET_BASE_URL
        self.footer_text = settings.EMAIL_FOOTER_TEXT

    def _build_html_body(
        self,
        ticket_id: int,
        ticket_title: str,
        requester_name: str,
        status_label: str,
        assigned_to: str,
        content_html: str,
    ) -> str:
        ticket_url = f"{self.ticket_base_url}{ticket_id}"

        # O campo 'content' do GLPI já vem em HTML (é o mesmo texto que o
        # Formcreator monta pra qualquer formulário), mas precisa ser
        # simplificado antes de embutir — HTML rico direto do GLPI pode
        # quebrar o parser de alguns clientes de email (Outlook em
        # especial), fazendo aparecer as tags cruas na tela.
        conteudo = simplify_form_content(content_html) or "<em>Sem conteúdo adicional.</em>"

        return f"""\
<html>
  <head>
    <meta charset="utf-8">
  </head>
  <body style="margin:0; padding:20px; background-color:#eef1f4; font-family: Arial, Helvetica, sans-serif; color:#2c3e50;">
    <div style="max-width: 560px; margin: 0 auto; background-color:#ffffff; border-radius: 8px; overflow: hidden; border: 1px solid #dfe3e8;">

      <div style="background-color:#26344b; color:#ffffff; padding: 20px 24px;">
        <h2 style="margin:0; font-size: 17px; font-weight: 700; line-height: 1.4;">
          Novo Chamado: {ticket_title}
        </h2>
      </div>

      <div style="padding: 22px 24px 8px 24px;">
        <table style="width:100%; border-collapse: collapse; font-size: 14px; margin-bottom: 18px;">
          <tr>
            <td style="padding: 4px 0;">👤 <strong>Requerente:</strong> {requester_name}</td>
          </tr>
          <tr>
            <td style="padding: 4px 0;">📶 <strong>Status:</strong> {status_label}</td>
          </tr>
          <tr>
            <td style="padding: 4px 0;">👥 <strong>Atribuído:</strong> {assigned_to}</td>
          </tr>
        </table>

        <div style="background-color:#f6f7f9; border: 1px solid #e5e8eb; border-radius: 6px; padding: 16px 18px; margin-bottom: 22px;">
          <div style="color:#b5651d; font-size: 13px; font-weight: 600; margin-bottom: 10px;">
            📋 Dados do Formulário:
          </div>
          <div style="font-size: 14px; line-height: 1.6; color:#2c3e50;">
            {conteudo}
          </div>
        </div>

        <div style="text-align:center; margin-bottom: 20px;">
          <a href="{ticket_url}"
             style="background-color:#2f80ed; color:#ffffff; text-decoration:none;
                    padding: 11px 26px; border-radius: 5px; font-size: 14px; font-weight: 600; display:inline-block;">
            Ver Chamado Completo
          </a>
        </div>
      </div>

      <div style="background-color:#f6f7f9; color:#8a94a3; font-size: 11px; text-align:center; padding: 10px 20px; border-top: 1px solid #e5e8eb;">
        {self.footer_text}
      </div>
    </div>
  </body>
</html>
"""

    def send_new_ticket_notification(
        self,
        ticket_id: int,
        ticket_title: str,
        requester_name: str,
        requester_email: str,
        status_label: str = "Novo",
        assigned_to: str = "Não atribuído",
        content_html: str = "",
        attachments: list[tuple[str, bytes]] | None = None,
    ) -> bool:
        if not self.recipients:
            logger.warning("⚠️ NOTIFICATION_RECIPIENTS não configurado — email não enviado.")
            return False

        if not self.user or not self.password:
            logger.error("❌ SMTP_USER / SMTP_PASSWORD não configurados.")
            return False

        try:
            # "mixed" por fora pra poder ter anexo real; o corpo (html) fica
            # dentro de uma sub-parte "alternative"
            msg = MIMEMultipart("mixed")
            msg["Subject"] = f"[GLPI #{ticket_id}] Novo chamado {ticket_title}"
            msg["From"] = formataddr((self.from_name, self.from_email))
            msg["To"] = ", ".join(self.recipients)

            cc_list = []
            if self.notify_cc_requester and requester_email:
                cc_list.append(requester_email)
                msg["Cc"] = ", ".join(cc_list)

            html_body = self._build_html_body(
                ticket_id=ticket_id,
                ticket_title=ticket_title,
                requester_name=requester_name,
                status_label=status_label,
                assigned_to=assigned_to,
                content_html=content_html,
            )

            alt_part = MIMEMultipart("alternative")
            alt_part.attach(MIMEText(html_body, "html", "utf-8"))
            msg.attach(alt_part)

            # CORREÇÃO: Processamento correto dos anexos
            for filename, file_bytes in (attachments or []):
                try:
                    # Garante que file_bytes seja bytes
                    if not isinstance(file_bytes, bytes):
                        logger.warning(f"⚠️ Conteúdo do anexo '{filename}' não é bytes: {type(file_bytes)}")
                        continue
                    
                    # Detecta o tipo MIME do arquivo
                    content_type, encoding = mimetypes.guess_type(filename)
                    if content_type is None:
                        content_type = "application/octet-stream"
                    
                    # Cria a parte do anexo
                    part = MIMEBase(*content_type.split('/'))
                    part.set_payload(file_bytes)
                    encoders.encode_base64(part)
                    
                    # Adiciona o cabeçalho Content-Disposition
                    part.add_header(
                        "Content-Disposition",
                        f"attachment",
                        filename=filename
                    )
                    msg.attach(part)
                    logger.info(f"📎 Anexo adicionado ao email: {filename} ({len(file_bytes)} bytes)")

                except Exception as e:
                    logger.warning(f"Erro ao anexar arquivo '{filename}' no email: {e}")

            all_recipients = self.recipients + cc_list

            with smtplib.SMTP(self.host, self.port, timeout=30) as server:
                server.starttls()
                server.login(self.user, self.password)
                server.sendmail(self.from_email, all_recipients, msg.as_string())

            logger.info(
                f"✅ Email enviado para o chamado #{ticket_id} ({requester_name}) "
                f"com {len(attachments or [])} anexo(s)"
            )
            return True

        except smtplib.SMTPAuthenticationError as e:
            logger.error(f"❌ Falha de autenticação SMTP: {e}")
            return False
        except Exception as e:
            logger.exception(f"❌ Erro ao enviar email do chamado #{ticket_id}: {e}")
            return False


email_service = EmailService()