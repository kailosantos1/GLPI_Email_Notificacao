# Configuração — `config.py`

Arquivo: [`config.py`](../../../config.py).

## Carregamento

`BASE_DIR` é a pasta do executável quando o atributo `sys.frozen` está ativo; caso contrário, é a pasta de `config.py`. `load_dotenv()` procura `.env` nessa base. O módulo cria `settings` (instância de `Settings`) e o logger `GLPI_Notifier`.

O arquivo contém parâmetros de autenticação. Este vault não reproduz valores sensíveis. Como `config.py` é versionado, a forma de provisionar credenciais deve ser confirmada antes de publicar ou operar o serviço; consulte [[08 - Pendencias/Pontos a confirmar|Pontos a confirmar]].

## Parâmetros identificados

| Grupo | Nomes usados pelo código | Uso |
|---|---|---|
| GLPI | `GLPI_URL`, `GLPI_APP_TOKEN`, `GLPI_USER_TOKEN` | Inicialização de sessão e consultas REST |
| URL do ticket | `GLPI_TICKET_BASE_URL` | Link direto incluído no e-mail |
| Polling | `POLL_INTERVAL_SECONDS`, `NOTIFY_DELAY_SECONDS`, `GLPI_FETCH_PAGE_SIZE` | Frequência, espera antes de notificar e tamanho da página |
| Estado | `STATE_FILE`, `SKIP_BACKLOG_ON_FIRST_RUN` | Caminho do checkpoint e política de primeira execução |
| SMTP | `SMTP_HOST`, `SMTP_PORT`, `SMTP_USER`, `SMTP_PASSWORD`, `SMTP_FROM_NAME`, `SMTP_FROM_EMAIL` | Conexão e identificação do remetente |
| Destinatários | `NOTIFICATION_RECIPIENTS`, `NOTIFY_CC_REQUESTER` | Lista de destinatários e cópia opcional ao requerente |
| Mensagem | `EMAIL_FOOTER_TEXT` | Texto do rodapé |

O código define defaults para vários parâmetros operacionais; eles são valores de fallback, não configuração recomendada universal. Credenciais e endpoints sensíveis não são copiados. Destinatários são separados por vírgula e normalizados com `strip()`.

Defaults operacionais não sensíveis confirmados no fonte: polling de 60 segundos, espera pré-notificação de 10 segundos, página GLPI de 200 itens, `SKIP_BACKLOG_ON_FIRST_RUN=true`, estado em `state.json` na base de execução quando `STATE_FILE` não é sobrescrito, SMTP na porta 587 e cópia ao requerente habilitada. São valores de fallback do código, não validação de que sejam adequados ao ambiente.

## Relações

- Consumida por [[02 - Modulos/Orquestrador|`main.py`]] e pelos dois serviços.
- O estado é descrito em [[04 - Dados/Checkpoint local|Checkpoint local]].
- Instruções para operação: [[06 - Desenvolvimento/Configuracao e execucao|Configuração e execução]].

Voltar para [[02 - Modulos/Indice|Índice de Módulos]].
