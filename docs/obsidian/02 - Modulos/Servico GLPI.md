# Serviço GLPI

Implementação: [`services/glpi_service.py`](../../../services/glpi_service.py).

## Responsabilidades

`GLPIService` encapsula as chamadas REST necessárias para obter tickets, status, atores, grupos e documentos. Usa `requests` e cabeçalhos de sessão GLPI.

Métodos relevantes:

- `get_session_headers()` abre sessão via `initSession`.
- `kill_session(headers)` solicita encerramento.
- `_fetch_all_ticket_ids(headers)` pagina `/Ticket`; usa `GLPI_FETCH_PAGE_SIZE` e contém limite de segurança de 20.000 posições.
- `get_new_tickets(last_id, headers)` filtra IDs acima do cursor, ordena e busca detalhes sequencialmente.
- `get_ticket_requester()` resolve o ator do tipo requerente e delega dados de usuário.
- `get_ticket_assigned()` tenta grupo atribuído e depois técnico individual.
- `get_ticket_documents()` descobre documentos relacionados ao ticket e solicita seus bytes a `get_document_file()`.

## Status

O mapa `TICKET_STATUS_MAP` associa os códigos 1 a 6 a rótulos legíveis: Novo, Em atendimento (atribuído), Em atendimento (planejado), Pendente, Solucionado e Fechado. Valor inválido ou não mapeado recebe rótulo de fallback.

## Limites de falha observados

Os métodos convertem vários erros HTTP/exceções em logs e valores vazios ou de fallback. Por isso, um ciclo pode continuar com dados do requerente, atribuição ou anexos incompletos; uma falha ao buscar detalhes de um ticket pode fazer aquele detalhe não entrar na lista retornada. A camada de orquestração e suas regras estão em [[02 - Modulos/Orquestrador|`main.py`]].

## Relações

- Fluxo consumidor: [[03 - Fluxos/Notificacao|Notificação de ticket]].
- Contratos externos: [[05 - Interfaces e Integracoes/API REST do GLPI|API REST do GLPI]].
- Serviço complementar: [[02 - Modulos/Servico de email|Envio de e-mail]].

Voltar para [[02 - Modulos/Indice|Índice de Módulos]].
