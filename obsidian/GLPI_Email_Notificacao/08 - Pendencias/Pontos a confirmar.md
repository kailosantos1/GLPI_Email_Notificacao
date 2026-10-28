# Pontos a confirmar

Esta nota distingue fatos visíveis no repositório de decisões ou condições que só o mantenedor/operador pode validar.

## Divergências confirmadas

1. **Versão de Python:** README declara Python 3.8+, mas o fonte usa sintaxe de união `|`, que requer Python 3.10+. Atualizar a declaração mínima após confirmar a versão de runtime pretendida.
2. **Manifesto de dependências:** README cita `requirements.txt`; o arquivo versionado chama-se `requirements` (sem extensão). Os comandos nesta documentação usam o nome encontrado.
3. **Parâmetros documentados no README:** comparar a lista do README com as chaves realmente consumidas em `config.py`; por exemplo, o código define `GLPI_FETCH_PAGE_SIZE`, `SMTP_HOST`, `NOTIFICATION_RECIPIENTS` e outros parâmetros que não aparecem de forma consistente no exemplo original. Confirmar e harmonizar o modelo de configuração sem publicar segredos.

## Confirmações operacionais necessárias

- Confirmar versão e configuração da API GLPI: o código depende de endpoints e formatos específicos, mas não declara uma versão suportada.
- Confirmar provisionamento das credenciais. `config.py` é versionado e contém atribuições para credenciais; valores não são reproduzidos neste vault. Se valores válidos tiverem sido commitados, tratar como possível exposição e rotacioná-los; preferir provisionamento fora do Git.
- Confirmar qual deve ser o comportamento quando a primeira tentativa de determinar o maior ticket falha: o código salva cursor zero, o que pode processar backlog depois.
- Confirmar se a busca integral de IDs em cada ciclo e o limite de segurança de 20.000 posições atendem ao volume esperado.
- Confirmar se falha ao baixar anexo deve permitir o envio sem ele. O comportamento atual pode enviar a notificação sem todos os anexos.
- Confirmar a estratégia de backup/recuperação do estado e a supervisão do processo.
- Confirmar se deseja implementar testes automatizados e um processo de build/deploy; não foram encontrados no repositório.

## Limites desta análise

- Não foram lidos `.env`, arquivos gerados, caches, ambientes instalados ou binários.
- Nenhuma chamada de rede, teste integrado, build ou envio de e-mail foi executado.
- O conjunto de arquivos versionados é pequeno e foi examinado diretamente; o inventário está descrito em [[00 - Inicio/Inicio|Início]].

Voltar para [[08 - Pendencias/Indice|Índice de Pendências]] · [[00 - Inicio/Inicio|Início]].
