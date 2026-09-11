# main.py
"""
GLPI Email Notifier
--------------------
Fica monitorando o GLPI em intervalos (POLL_INTERVAL_SECONDS) e envia um
email de notificação para cada chamado novo encontrado, com o requerente
correto (lido diretamente do ticket, já com os atores certos).

Roda separado do bot do Teams — projeto independente.

Uso:
    python main.py
    (Ctrl+C para parar)
"""

import json
import re
import time
import signal
import sys
from pathlib import Path

from config import settings, logger
from services.glpi_service import GLPIService
from services.email_service import email_service

glpi_service = GLPIService()

_running = True


def _handle_shutdown(signum, frame):
    global _running
    logger.info("🛑 Sinal de encerramento recebido, finalizando após o ciclo atual...")
    _running = False


signal.signal(signal.SIGINT, _handle_shutdown)
signal.signal(signal.SIGTERM, _handle_shutdown)


def _interruptible_sleep(seconds: int) -> None:
    """Dorme em passos de 1s, checando _running, pra Ctrl+C não travar no meio da espera."""
    for _ in range(seconds):
        if not _running:
            break
        time.sleep(1)


# ---------------------------------------------------------------------------
# Persistência do estado (último ticket processado)
# ---------------------------------------------------------------------------
def load_last_id() -> int:
    state_path = Path(settings.STATE_FILE)
    if not state_path.exists():
        return -1  # sinaliza "primeira execução"

    try:
        with open(state_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            return int(data.get("last_ticket_id", 0))
    except Exception as e:
        logger.warning(f"Não foi possível ler {state_path}, começando do zero: {e}")
        return 0


def save_last_id(last_id: int) -> None:
    state_path = Path(settings.STATE_FILE)
    try:
        with open(state_path, "w", encoding="utf-8") as f:
            json.dump({"last_ticket_id": last_id}, f)
    except Exception as e:
        logger.error(f"Erro ao salvar estado em {state_path}: {e}")


# ---------------------------------------------------------------------------
# Ciclo principal
# ---------------------------------------------------------------------------
def run_cycle(last_id: int) -> int:
    """Executa um ciclo de verificação. Retorna o novo last_id."""
    headers = glpi_service.get_session_headers()
    if not headers:
        logger.error("Não foi possível abrir sessão no GLPI neste ciclo. Tentando de novo no próximo.")
        return last_id

    try:
        novos_tickets = glpi_service.get_new_tickets(last_id, headers)

        if not novos_tickets:
            logger.info(f"Nenhum ticket novo (último conhecido: {last_id}).")
            return last_id

        logger.info(f"🎫 {len(novos_tickets)} ticket(s) novo(s) encontrado(s).")

        for ticket in novos_tickets:
            ticket_id = int(ticket["id"])
            ticket_title = ticket.get("name", "(sem título)")

            logger.info(f"🆕 Ticket novo detectado: #{ticket_id} - '{ticket_title}'. Aguardando {settings.NOTIFY_DELAY_SECONDS}s antes de notificar...")
            _interruptible_sleep(settings.NOTIFY_DELAY_SECONDS)

            if not _running:
                logger.info("Encerramento solicitado durante a espera — email não enviado, será tentado no próximo ciclo.")
                break

            requester_name, requester_email = glpi_service.get_ticket_requester(ticket_id, headers)
            status_label = glpi_service.get_ticket_status_label(ticket.get("status"))
            assigned_to = glpi_service.get_ticket_assigned(ticket_id, headers)
            content_html = ticket.get("content", "")

            # ============================================================
            # CORREÇÃO AQUI: Busca os documentos anexados ao ticket
            # ============================================================
            logger.info(f"📎 Buscando documentos anexados ao ticket #{ticket_id}...")
            attachments = glpi_service.get_ticket_documents(ticket_id, headers)
            
            if attachments:
                logger.info(f"📎 {len(attachments)} anexo(s) encontrado(s) para o ticket #{ticket_id}")
                for filename, data in attachments:
                    logger.info(f"  - {filename} ({len(data)} bytes)")
            else:
                logger.info(f"📎 Nenhum anexo encontrado para o ticket #{ticket_id}")
            # ============================================================

            logger.info(f"➡️  Ticket #{ticket_id} - '{ticket_title}' - Requerente: {requester_name} ({requester_email})")

            enviado = email_service.send_new_ticket_notification(
                ticket_id=ticket_id,
                ticket_title=ticket_title,
                requester_name=requester_name,
                requester_email=requester_email,
                status_label=status_label,
                assigned_to=assigned_to,
                content_html=content_html,
                attachments=attachments,  # <-- Agora com os anexos
            )

            if enviado:
                # Só avança o checkpoint se o email realmente saiu
                last_id = ticket_id
                save_last_id(last_id)
            else:
                logger.warning(
                    f"⚠️ Email do ticket #{ticket_id} falhou — checkpoint não avançado, "
                    f"vai tentar de novo no próximo ciclo."
                )
                break  # para o ciclo aqui pra manter a ordem e tentar de novo depois

        return last_id

    finally:
        glpi_service.kill_session(headers)


def main():
    logger.info("=" * 60)
    logger.info("GLPI Email Notifier - iniciando")
    logger.info(f"Intervalo de verificação: {settings.POLL_INTERVAL_SECONDS}s")
    logger.info("=" * 60)

    last_id = load_last_id()

    if last_id == -1:
        # Primeira execução (sem state.json)
        if settings.SKIP_BACKLOG_ON_FIRST_RUN:
            headers = glpi_service.get_session_headers()
            if headers:
                last_id = glpi_service.get_latest_ticket_id(headers)
                glpi_service.kill_session(headers)
                logger.info(f"Primeira execução: pulando histórico, começando a partir do ticket #{last_id}.")
            else:
                last_id = 0
                logger.warning("Não foi possível determinar o último ticket na primeira execução, começando do 0.")
        else:
            last_id = 0
            logger.info("Primeira execução: SKIP_BACKLOG_ON_FIRST_RUN=false, processando histórico completo.")

        save_last_id(last_id)

    logger.info(f"Checkpoint inicial: último ticket processado = #{last_id}")

    while _running:
        try:
            last_id = run_cycle(last_id)
        except Exception as e:
            logger.exception(f"Erro inesperado no ciclo: {e}")

        _interruptible_sleep(settings.POLL_INTERVAL_SECONDS)

    logger.info("Encerrado.")
    sys.exit(0)


if __name__ == "__main__":
    main()