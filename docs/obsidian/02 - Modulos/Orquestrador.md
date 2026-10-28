# Orquestrador — `main.py`

Arquivo: [`main.py`](../../../main.py).

## Responsabilidades

- Instanciar `GLPIService` e usar o singleton `email_service`.
- Ler e salvar `last_ticket_id` em `load_last_id()` e `save_last_id()`.
- Coordenar um ciclo em `run_cycle(last_id)`.
- Tratar `SIGINT` e `SIGTERM` com `_handle_shutdown()` e aguardar o ciclo/espera interrompível terminar.
- Inicializar o cursor em `main()` e repetir ciclos no intervalo configurado.

## Regras de execução observadas

- Sem arquivo de estado, `load_last_id()` retorna `-1`, sinalizando primeira execução.
- Se `SKIP_BACKLOG_ON_FIRST_RUN` estiver habilitado, a inicialização consulta o maior ID atual e salva esse cursor antes do polling. Se não estiver, começa em zero.
- No ciclo, o cursor só avança e é salvo quando o envio do e-mail retorna sucesso.
- Se o envio falha, o processamento da sequência para; o ticket não é confirmado e será elegível novamente no próximo ciclo.
- A sessão do GLPI é encerrada no bloco `finally` de `run_cycle()`.

O caso inicial de falha ao abrir sessão para determinar o backlog segue uma regra distinta: define o cursor como zero, salva-o e registra aviso. Veja [[03 - Fluxos/Notificacao|o fluxo detalhado]] e [[04 - Dados/Checkpoint local|o formato do estado]].

## Dependências internas

- [[02 - Modulos/Configuracao|`config.py`]]
- [[02 - Modulos/Servico GLPI|`GLPIService`]]
- [[02 - Modulos/Servico de email|`EmailService`]]

Voltar para [[02 - Modulos/Indice|Índice de Módulos]].
