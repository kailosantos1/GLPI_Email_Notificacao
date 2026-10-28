# Checkpoint local

O estado persistente é um arquivo JSON definido por `STATE_FILE`, configurado em [`config.py`](../../../config.py). O padrão do código aponta para `state.json` junto à base de execução (`BASE_DIR`); o `.gitignore` também exclui `state.json`.

## Formato

`save_last_id(last_id)` escreve um objeto com a chave `last_ticket_id`, cujo valor é o identificador do último ticket cujo e-mail foi enviado com sucesso.

```json
{
  "last_ticket_id": 123
}
```

O número acima é apenas um exemplo de formato, não dado real do projeto.

## Leitura e inicialização

- Arquivo ausente: `load_last_id()` retorna `-1` para sinalizar primeira execução.
- JSON ilegível ou valor que não possa ser convertido: registra aviso e retorna `0`.
- Primeira execução com `SKIP_BACKLOG_ON_FIRST_RUN=true`: consulta o maior ID existente, salva o cursor e não envia notificações retroativas.
- Primeira execução com a opção falsa: começa em `0` e pode percorrer os tickets existentes.
- Durante a operação, a gravação acontece após cada envio bem-sucedido.

## Implicações

O arquivo é um cursor simples, não uma fila nem um histórico de entregas. Falha no envio não avança o cursor daquele ticket e interrompe o processamento dos tickets seguintes no mesmo ciclo. O método de gravação captura erros e registra log, mas não propaga o erro para `run_cycle()`.

Veja [[03 - Fluxos/Notificacao|fluxo completo]], [[02 - Modulos/Configuracao|parâmetros]] e [[07 - Operacao/Execucao e recuperacao|recuperação operacional]].

Voltar para [[04 - Dados/Indice|Índice de Dados]].
