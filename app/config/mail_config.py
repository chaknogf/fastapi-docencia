from fastapi_mail import ConnectionConfig

conf = ConnectionConfig(
    MAIL_USERNAME="ticshosptecpan@gmail.com",
    MAIL_PASSWORD="gdjv zqbu zorp ifau",            # App Password
    MAIL_FROM="ticshosptecpan@gmail.com",
    MAIL_PORT=587,
    MAIL_SERVER="smtp.gmail.com",
    USE_CREDENTIALS=True,
    VALIDATE_CERTS=True,
    MAIL_STARTTLS=True,     # STARTTLS en puerto 587
    MAIL_SSL_TLS=False      # No SSL directo
)
# Si usaras puerto 465 con SSL, sería:
# MAIL_PORT=465,
# MAIL_STARTTLS=False,
# MAIL_SSL_TLS=True