# Testes e validação

## O que existe no repositório

Não foram encontrados arquivos de teste, configuração de `pytest`/`tox`, pipeline CI ou tarefa de build. O inventário versionado contém apenas a aplicação e seus serviços, configuração, README, dependências e arquivos Git.

O `.gitignore` menciona artefatos de PyInstaller (`build/`, `dist/`, `*.exe`, `*.spec`), e `config.py` trata execução congelada, mas não foi encontrada configuração ou comando de empacotamento que confirme um processo de build suportado.

## Validações desta documentação

Na geração do vault, a validação cobre:

- JSON de configuração `.obsidian/app.json` bem-formado.
- Links Obsidian `[[...]]` resolvidos para notas existentes.
- Links Markdown locais para arquivos existentes.
- Inclusão de cada nota nos índices da sua pasta.

As validações estáticas não substituem testes de integração. Nenhum acesso à API GLPI ou servidor SMTP foi realizado.

## Recomendações para validação de software

Antes de adotar testes automatizados, confirmar ambiente e versões do GLPI/SMTP, credenciais de teste e se há ambiente isolado. Não executar o poller contra produção para testar alterações sem autorização operacional explícita.

Voltar para [[06 - Desenvolvimento/Indice|Índice de Desenvolvimento]] · [[08 - Pendencias/Pontos a confirmar|Pontos a confirmar]].
