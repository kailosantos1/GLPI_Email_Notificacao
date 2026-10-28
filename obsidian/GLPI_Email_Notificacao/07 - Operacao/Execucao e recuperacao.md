# Execução e recuperação

## Ciclo de vida

O ponto de entrada é `python3 main.py` (ver [[06 - Desenvolvimento/Configuracao e execucao|execução]]). O programa roda um loop de polling e registra logs em nível INFO. `Ctrl+C` (`SIGINT`) e `SIGTERM` definem uma flag de encerramento; a espera é interrompível e o ciclo termina antes do encerramento, salvo interrupção durante o delay de notificação, quando o e-mail daquele ticket é adiado.

## Recuperação

- O cursor salvo em `state.json` permite retomar a partir do último envio bem-sucedido.
- Falha ao abrir uma sessão durante um ciclo mantém o cursor.
- Falha de envio deixa o ticket sem confirmação e para o processamento dos seguintes no ciclo.
- O método que salva o estado registra erro, mas não propaga a falha; portanto, uma falha de gravação pode deixar o cursor persistido atrás do e-mail já enviado.
- Se o estado não puder ser interpretado, o código volta ao cursor zero; isso pode tornar tickets anteriores elegíveis para envio novamente.

## Diagnóstico

Use os logs do processo para observar erros de sessão, listagem, detalhes, documentos e SMTP. As mensagens de erro de respostas HTTP podem incluir texto retornado pelo servidor; ao compartilhar logs, revisar e remover dados pessoais ou sensíveis.

Não há documentação de deploy, serviço de sistema, supervisão de processo, rotação de logs, métricas ou alertas. A implantação nesses moldes depende de definição operacional.

Mais detalhes: [[03 - Fluxos/Notificacao|fluxo]], [[04 - Dados/Checkpoint local|estado]] e [[08 - Pendencias/Pontos a confirmar|limitações e perguntas]].

Voltar para [[07 - Operacao/Indice|Índice de Operação]].
