# test_email.py
"""
Script de teste isolado do envio de email de notificação de novo chamado.

Roda separado do bot do Teams e do GLPI — serve só para validar que o
SMTP está autenticando certo e que o template do email está bom, com
dados fictícios.

Uso:
    python test_email.py
"""

from services.email_service import email_service


def main():
    print("=" * 60)
    print("TESTE - Envio de email de notificação de chamado")
    print("=" * 60)

    # Dados fictícios, só pra teste
    resultado = email_service.send_new_ticket_notification(
        ticket_id=999,
        requester_name="Kailo Teste",
        requester_email="kailo.systemup@gmail.com",
        tipo="Manutenção de Sistemas",
        equipamento="Sistemas/Softwares",
        descricao="Este é um chamado de TESTE gerado pelo test_email.py",
        filial="Maravilha",
        canal="Microsoft Teams",
    )

    print("=" * 60)
    if resultado:
        print("✅ SUCESSO — email enviado. Confira a caixa de entrada configurada em NOTIFICATION_RECIPIENTS.")
    else:
        print("❌ FALHA — email não foi enviado. Confira os logs acima para o motivo (auth, recipients vazio, etc).")
    print("=" * 60)


if __name__ == "__main__":
    main()