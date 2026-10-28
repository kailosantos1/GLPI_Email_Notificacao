# Serviço de e-mail

Implementação: [`services/email_service.py`](../../../services/email_service.py).

## Responsabilidades

`EmailService` recebe os dados preparados pelo orquestrador, compõe a mensagem MIME e transmite a notificação usando SMTP com STARTTLS.

- `simplify_form_content(raw_html)` reduz o conteúdo HTML do formulário, normaliza algumas estruturas e converte imagens/anexos referenciados em links absolutos do GLPI.
- `_build_html_body(...)` constrói o corpo HTML com título, requerente, status, atribuição, conteúdo e link para o ticket.
- `send_new_ticket_notification(...)` monta a mensagem, inclui anexos binários e envia para a lista configurada.

## Destinatários e anexos

Se `NOTIFICATION_RECIPIENTS` estiver vazia ou as credenciais SMTP esperadas pelo serviço não estiverem configuradas, o método retorna `False`. Se `NOTIFY_CC_REQUESTER` estiver ativo e o requerente tiver e-mail, ele é incluído em cópia.

Os anexos recebidos como pares `(filename, bytes)` são adicionados como partes MIME; o tipo é inferido pela extensão, com fallback para `application/octet-stream`. Falhas individuais ao anexar são registradas, mas não necessariamente impedem o envio da mensagem.

## Relações

- É invocado por [[02 - Modulos/Orquestrador|`main.py`]].
- Usa dados vindos de [[02 - Modulos/Servico GLPI|`GLPIService`]].
- Contrato de transporte: [[05 - Interfaces e Integracoes/SMTP|SMTP]].

Voltar para [[02 - Modulos/Indice|Índice de Módulos]].
