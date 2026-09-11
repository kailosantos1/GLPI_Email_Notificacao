# config.py
import os
import sys
import logging
from pathlib import Path
from dotenv import load_dotenv

# Quando empacotado como .exe (PyInstaller), __file__ aponta pra uma pasta
# temporária interna do executável — precisamos usar a pasta onde o .exe
# de verdade está (sys.executable) pra achar o .env e o state.json do lado dele.
if getattr(sys, "frozen", False):
    BASE_DIR = Path(sys.executable).parent
else:
    BASE_DIR = Path(__file__).parent

# Carrega o .env que fica do lado do .exe (ou do script, em dev)
load_dotenv(dotenv_path=BASE_DIR / ".env")

# ---------------------------------------------------------------------------
# Logger
# ---------------------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] GLPI_Notifier: %(message)s",
)
logger = logging.getLogger("GLPI_Notifier")


class Settings:
    # -----------------------------------------------------------------
    # GLPI - API REST
    # -----------------------------------------------------------------
    GLPI_URL = os.getenv("GLPI_URL", "http://177.38.10.100:8081/apirest.php")
    GLPI_APP_TOKEN = os.getenv("GLPI_APP_TOKEN")
    GLPI_USER_TOKEN = os.getenv("GLPI_USER_TOKEN")

    # URL base pra montar o link direto do chamado no email
    GLPI_TICKET_BASE_URL = os.getenv(
        "GLPI_TICKET_BASE_URL",
        "http://177.38.10.100:8081/front/ticket.form.php?id=",
    )

    # -----------------------------------------------------------------
    # Polling - de quanto em quanto tempo verifica novos chamados
    # -----------------------------------------------------------------
    POLL_INTERVAL_SECONDS = int(os.getenv("POLL_INTERVAL_SECONDS", "60"))

    # Quantos segundos esperar, depois de detectar um ticket novo, antes de
    # mandar o email (dá tempo do GLPI terminar de processar o chamado)
    NOTIFY_DELAY_SECONDS = int(os.getenv("NOTIFY_DELAY_SECONDS", "10"))

    # Quantos tickets buscar por página durante a paginação (a busca varre
    # TODAS as páginas até acabar, isso só controla o tamanho de cada request)
    GLPI_FETCH_PAGE_SIZE = int(os.getenv("GLPI_FETCH_PAGE_SIZE", "200"))

    # Arquivo onde fica salvo o ID do último ticket já notificado,
    # para não reenviar email em caso de restart do script
    STATE_FILE = os.getenv("STATE_FILE", str(BASE_DIR / "state.json"))

    # Se True, na primeira execução (sem state.json) o script NÃO manda
    # email retroativo de todo o histórico — só começa a notificar
    # tickets criados a partir de agora. Se False, ele processa também
    # os tickets já existentes na primeira execução.
    SKIP_BACKLOG_ON_FIRST_RUN = os.getenv("SKIP_BACKLOG_ON_FIRST_RUN", "true").lower() == "true"

    # -----------------------------------------------------------------
    # SMTP - envio de notificação de novo chamado
    # -----------------------------------------------------------------
    SMTP_HOST = os.getenv("SMTP_HOST", "smtp.gmail.com")
    SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
    SMTP_USER = os.getenv("SMTP_USER")
    SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")
    SMTP_FROM_NAME = os.getenv("SMTP_FROM_NAME", "GLPI - Compasi")
    SMTP_FROM_EMAIL = os.getenv("SMTP_FROM_EMAIL", SMTP_USER)

    NOTIFICATION_RECIPIENTS = [
        e.strip() for e in os.getenv("NOTIFICATION_RECIPIENTS", "").split(",") if e.strip()
    ]

    NOTIFY_CC_REQUESTER = os.getenv("NOTIFY_CC_REQUESTER", "true").lower() == "true"

    # Texto do rodapé do email (ex: "TI SystemUp - Notificação Automática")
    EMAIL_FOOTER_TEXT = os.getenv("EMAIL_FOOTER_TEXT", "TI Compasi - Notificação Automática")


settings = Settings()