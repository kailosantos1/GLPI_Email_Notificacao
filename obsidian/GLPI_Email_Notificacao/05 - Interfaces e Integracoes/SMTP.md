# SMTP

O `EmailService` conecta ao servidor configurado por `SMTP_HOST` e `SMTP_PORT`, inicia STARTTLS, autentica com os parâmetros SMTP e chama `sendmail()`. A implementação usa `smtplib` e classes MIME da biblioteca padrão.

## Mensagem

- Assunto com ID e título do ticket.
- Remetente configurado por `SMTP_FROM_NAME` e `SMTP_FROM_EMAIL`.
- Destinatários em `NOTIFICATION_RECIPIENTS`.
- Cópia opcional ao requerente conforme `NOTIFY_CC_REQUESTER`.
- Corpo HTML e anexos reais obtidos no GLPI.

As opções de TLS, host, porta, usuário e remetente são parâmetros do projeto. O repositório não documenta um servidor SMTP validado nem prova conectividade/autenticação no ambiente de execução.

Veja [[02 - Modulos/Servico de email|Serviço de e-mail]], [[02 - Modulos/Configuracao|Configuração]] e [[03 - Fluxos/Notificacao|Fluxo de envio]].

Voltar para [[05 - Interfaces e Integracoes/Indice|Índice de Integrações]].
