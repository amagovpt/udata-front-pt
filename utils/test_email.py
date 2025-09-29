# test_email.py

## Teste simples de envio de e-mail usando pytest e smtplib
## Crie um ambiente virtual e instale pytest:
## python -m venv venv
## source venv/bin/activate
## pip install pytest
## Execute o teste com:
## pytest -v test_email.py

import smtplib
from email.mime.text import MIMEText
import pytest

# Configurações
MAIL_SERVER = "mail.ama.pt"
MAIL_DEFAULT_SENDER = "noreply.dados.gov@ama.gov.pt"
MAIL_DEFAULT_RECEIVER = "dados@ama.pt"
MAIL_PORT = 25
MAIL_USE_TLS = False
MAIL_USE_SSL = False


@pytest.mark.parametrize("receiver", [
    MAIL_DEFAULT_RECEIVER,
    "emailtest@gmail.com", # adiciona um gmail para testar
])
def test_enviar_email(receiver):
    """Teste simples de envio de e-mail com as configurações fornecidas."""

    msg = MIMEText("Teste de envio de e-mail via Python/pytest.")
    msg["Subject"] = "Teste Pytest"
    msg["From"] = MAIL_DEFAULT_SENDER
    msg["To"] = receiver

    try:
        if MAIL_USE_SSL:
            smtp = smtplib.SMTP_SSL(MAIL_SERVER, MAIL_PORT)
        else:
            smtp = smtplib.SMTP(MAIL_SERVER, MAIL_PORT, timeout=10)

        if MAIL_USE_TLS:
            smtp.starttls()

        # Caso haja autenticação necessária (não definida aqui),
        # podes adicionar smtp.login("user", "password")

        smtp.sendmail(MAIL_DEFAULT_SENDER, [receiver], msg.as_string())
        smtp.quit()

        assert True  # se chegou aqui, o envio foi feito sem erro

    except Exception as e:
        pytest.fail(f"Falha ao enviar email para {receiver}: {e}")
