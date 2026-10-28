# GLPI Email Notifier

Este vault documenta o serviço Python que consulta tickets novos no GLPI e envia notificações por e-mail com dados do chamado e arquivos anexados.

## Comece por aqui

- [[01 - Arquitetura/Visao geral|Arquitetura e tecnologias]]
- [[02 - Modulos/Indice|Módulos e responsabilidades]]
- [[03 - Fluxos/Notificacao|Fluxo de notificação]]
- [[04 - Dados/Checkpoint local|Checkpoint e persistência]]
- [[05 - Interfaces e Integracoes/Indice|Interfaces e integrações]]
- [[06 - Desenvolvimento/Indice|Configuração, execução e testes]]
- [[07 - Operacao/Execucao e recuperacao|Operação e recuperação]]
- [[08 - Pendencias/Pontos a confirmar|Dúvidas e limitações]]

## Mapa do vault

- [[01 - Arquitetura/Indice|01 — Arquitetura]]
- [[02 - Modulos/Indice|02 — Módulos]]
- [[03 - Fluxos/Indice|03 — Fluxos]]
- [[04 - Dados/Indice|04 — Dados]]
- [[05 - Interfaces e Integracoes/Indice|05 — Interfaces e integrações]]
- [[06 - Desenvolvimento/Indice|06 — Desenvolvimento]]
- [[07 - Operacao/Indice|07 — Operação]]
- [[08 - Pendencias/Indice|08 — Pendências]]

## Escopo e critérios

A documentação foi elaborada a partir dos arquivos versionados do repositório: `main.py`, `config.py`, `services/`, `requirements`, `.gitignore` e `README.md`. Arquivos gerados, ambientes instalados, caches e arquivos `.env` não foram usados como fonte.

As afirmações descrevem o código e a configuração observados. Divergências entre documentação existente e código, ausência de componentes e questões dependentes do ambiente estão identificadas em [[08 - Pendencias/Pontos a confirmar|Pontos a confirmar]]. Nenhuma credencial ou valor de segredo é reproduzido aqui.

## Fontes principais

- [`main.py`](../../../main.py) — loop e coordenação.
- [`config.py`](../../../config.py) — parâmetros e logger; contém configuração sensível que não é reproduzida.
- [`services/glpi_service.py`](../../../services/glpi_service.py) — leitura da API do GLPI.
- [`services/email_service.py`](../../../services/email_service.py) — composição e envio da notificação.
- [`requirements`](../../../requirements) — dependências declaradas.
- [`README.md`](../../../README.md) — documentação original do repositório.
