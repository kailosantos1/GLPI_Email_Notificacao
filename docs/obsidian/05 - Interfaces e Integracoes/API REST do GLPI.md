# API REST do GLPI

Cliente: [`services/glpi_service.py`](../../../services/glpi_service.py). A URL base é fornecida por `GLPI_URL`; as chamadas usam `requests`.

## Autenticação e sessão

O serviço inicia sessão por `POST /initSession`, enviando `App-Token` e autorização via user token. As chamadas seguintes usam o `Session-Token`; ao terminar o ciclo, solicita `GET /killSession`.

## Recursos chamados

| Operação | Endpoint relativo | Uso |
|---|---|---|
| Abrir/fechar sessão | `POST /initSession`, `GET /killSession` | Ciclo de sessão |
| Listar tickets | `GET /Ticket?range=...` | Paginação de IDs |
| Obter ticket | `GET /Ticket/{id}` | Dados e conteúdo |
| Atores | `GET /Ticket/{id}/Ticket_User` | Requerente e técnico |
| Usuário e e-mail | `GET /User/{id}`, `GET /User/{id}/UserEmail` | Identidade do ator |
| Grupo atribuído | `GET /Ticket/{id}/Group_Ticket`, `GET /Group/{id}` | Nome do grupo |
| Documentos do ticket | `GET /Ticket/{id}/Document_Item` | Relação ticket-documento |
| Baixar documento | `GET /Document/{id}` | Conteúdo binário |

O código aceita `200` ou `206` em algumas respostas paginadas/relacionadas e define timeouts por chamada. O contrato exato pode depender da versão e configuração do GLPI instaladas; não há versão de GLPI declarada no repositório.

## Dados consumidos

Os métodos interpretam IDs, `status`, `name`, `content`, tipos de ator, IDs de usuário/grupo, links de documentos e e-mail do usuário. Ator tipo `1` é tratado como requerente; tipo `2`, como atribuição.

## Relações

- Integração consumida por [[02 - Modulos/Servico GLPI|Serviço GLPI]].
- Sequência de chamadas: [[03 - Fluxos/Notificacao|Fluxo de notificação]].
- Configuração: [[02 - Modulos/Configuracao|Parâmetros do GLPI]].

Voltar para [[05 - Interfaces e Integracoes/Indice|Índice de Integrações]].
