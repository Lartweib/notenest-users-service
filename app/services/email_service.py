from aiosmtplib import SMTP
from email.message import EmailMessage
from app.core.config import settings

async def send_verification_email(to_email: str, verification_uuid: str, type: str = "register"):
    if type == "register":
        intro_message = "Gracias por registrarte."
    elif type == "change_email":
        intro_message = "Has solicitado cambiar tu email."
    verification_link = f"{settings.FRONTEND_URL}/verification/email/{verification_uuid}"
    email_content = f"""
    <html>
        <body style="text-align: center; font-family: Arial, sans-serif; background-color: #f9f9f9; padding: 20px;">
            <div style="background-color: #ffffff; padding: 40px; border-radius: 10px; box-shadow: 0px 0px 10px rgba(0, 0, 0, 0.1); display: inline-block;">
                <h2 style="color: #333;">Verifica tu dirección de correo electrónico</h2>
                <p>Hola,</p>
                <p>{intro_message} Por favor, haz clic en el botón de abajo para verificar tu dirección de correo electrónico:</p>
                <a href="{verification_link}" style="display: inline-block; padding: 15px 25px; margin-top: 20px; background-color: #4CAF50; color: white; text-decoration: none; font-weight: bold; border-radius: 5px;">Verificar Email</a>
                <p style="margin-top: 30px;">Si no puedes hacer clic en el botón, copia y pega el siguiente enlace en tu navegador:</p>
                <p><a href="{verification_link}" style="color: #4CAF50;">{verification_link}</a></p>
            </div>
        </body>
    </html>
    """

    message = EmailMessage()
    message['From'] = settings.SMTP_USERNAME
    message['To'] = to_email
    message['Subject'] = 'Verifica tu dirección de correo electrónico'
    message.set_content("Este es el mensaje de verificación. Por favor usa un cliente que soporte HTML para ver el contenido completo.")
    message.add_alternative(email_content, subtype='html')

    try:
        smtp = SMTP(hostname=settings.SMTP_HOST, port=settings.SMTP_PORT, use_tls=False)
        await smtp.connect()  
        await smtp.login(settings.SMTP_USERNAME, settings.SMTP_PASSWORD)
        await smtp.send_message(message)
        await smtp.quit()
    except Exception as e:
        print(f"Error enviando el correo: {e}")
