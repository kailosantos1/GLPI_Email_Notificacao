# Configuração e execução

## Requisitos

- Python 3.10 ou superior: o código usa sintaxe de tipo `dict | None` e `list[...]`. O README original diz Python 3.8+, mas essa declaração não é compatível com a sintaxe observada.
- Acesso à API REST do GLPI e a um servidor SMTP.
- Dependências listadas no arquivo [`requirements`](../../../requirements): `requests>=2.31.0` e `python-dotenv>=1.0.0`. Não há arquivo de lock versionado.

## Preparação

O manifesto de dependências se chama `requirements`, sem extensão `.txt`. O comando abaixo usa o nome efetivamente versionado:

```bash
python3 -m pip install -r requirements
```

Esse comando foi identificado a partir do manifesto, mas não executado nesta análise. Configure os parâmetros usados por `config.py` conforme o ambiente; consulte [[02 - Modulos/Configuracao|Parâmetros]] sem copiar credenciais para documentação ou controle de versão.

## Executar

```bash
python3 main.py
```

O comando é consistente com o ponto de entrada e foi identificado, mas não foi executado porque tentaria conectar a serviços externos e iniciar o polling contínuo.

## Arquivos de runtime

- `.env`: carregado na pasta-base do script ou executável; não foi lido nesta análise.
- `state.json`: checkpoint local, ignorado pelo Git.
- `requirements`: dependências.

O README refere-se a `requirements.txt`, mas o nome real versionado é `requirements`. Consulte [[07 - Operacao/Execucao e recuperacao|operação]] para primeira execução e retomada.

## Relações

- [[06 - Desenvolvimento/Testes e validacao|Validações]]
- [[08 - Pendencias/Pontos a confirmar|Divergências e decisões pendentes]]
- [[01 - Arquitetura/Visao geral|Tecnologias]]

Voltar para [[06 - Desenvolvimento/Indice|Índice de Desenvolvimento]].
