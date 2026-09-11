# 📧 GLPI Email Notifier

O **GLPI Email Notifier** é um serviço independente em Python que monitora o GLPI via API REST e envia notificações por e-mail para cada novo chamado aberto.

Ele identifica o requerente correto do chamado, recupera informações de status/atribuição, faz o download de todos os arquivos anexados ao ticket e inclui esses anexos diretamente no disparo do e-mail.

---

## 🚀 Funcionalidades

* 🔄 **Monitoramento Contínuo:** Checa a API do GLPI em intervalos configuráveis (`POLL_INTERVAL_SECONDS`).
* 📎 **Download e Envio de Anexos:** Recupera automaticamente os documentos vinculados aos tickets e os envia em anexo no e-mail.
* 👤 **Atores do Chamado:** Identifica com precisão o requerente e o técnico/grupo atribuído.
* ⏱️ **Delay Configurável:** Permite aguardar um tempo (`NOTIFY_DELAY_SECONDS`) antes do envio para dar tempo do usuário anexar todos os arquivos no GLPI.
* 💾 **Persistência de Estado:** Salva o ID do último ticket processado em um arquivo local (`state.json`) para evitar envios duplicados e perda de histórico.
* 🛑 **Encerramento Seguro (Graceful Shutdown):** Trata sinais de interrupção (`Ctrl+C` / `SIGTERM`) sem corromper o estado do ciclo atual.

---

## 🛠️ Pré-requisitos

* Python 3.8+
* Acesso à API REST do GLPI (App-Token e User-Token/Credentials)
* Servidor SMTP configurado para envio de e-mails

---

## 📂 Estrutura do Projeto

GLPI_EMAIL_NOTIFICACAO/
├── config.py              # Definições de variáveis de ambiente e logger
├── main.py                # Loop principal do serviço e controle de estado
├── requirements.txt       # Dependências do projeto
├── state.json             # (Gerado automaticamente) Armazena o ID do último ticket
├── services/
│   ├── email_service.py   # Lógica de montagem e envio dos e-mails
│   └── glpi_service.py    # Comunicação com a API REST do GLPI
└── .env                   # Variáveis de ambiente sensíveis (ignorado no Git)
---


## ⚙️ Configuração (.env)
Crie um arquivo .env na raiz do projeto com as credenciais do GLPI e do servidor SMTP:

Snippet de código
# Configurações do GLPI
GLPI_URL=[https://seu-glpi.com/apirest.php](https://seu-glpi.com/apirest.php)
GLPI_APP_TOKEN=seu_app_token
GLPI_USER_TOKEN=seu_user_token

# Configurações do serviço
POLL_INTERVAL_SECONDS=60
NOTIFY_DELAY_SECONDS=10
SKIP_BACKLOG_ON_FIRST_RUN=true
STATE_FILE=state.json

# Configurações de E-mail (SMTP)
SMTP_SERVER=smtp.office365.com
SMTP_PORT=587
SMTP_USER=seu-email@dominio.com
SMTP_PASSWORD=sua_senha
EMAIL_FROM=seu-email@dominio.com
---

## 💻 Como Executar
Instale as dependências:

Bash
pip install -r requirements.txt
Execute a aplicação:

Bash
python main.py
---