import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def send_email(to_email, subject, html_content):
    smtp_server = os.getenv("SMTP_SERVER", "smtp.gmail.com")
    smtp_port = int(os.getenv("SMTP_PORT", "465"))
    smtp_user = os.getenv("SMTP_EMAIL", "orbesrc@gmail.com")
    smtp_pass = os.getenv("SMTP_PASSWORD", "")
    
    if not smtp_pass:
        print("Advertencia: SMTP_PASSWORD no configurado. Correo no enviado.")
        return False
        
    msg = MIMEMultipart()
    msg['From'] = f"SKEL 360 <{smtp_user}>"
    msg['To'] = to_email
    msg['Subject'] = subject
    
    msg.attach(MIMEText(html_content, 'html'))
    
    try:
        with smtplib.SMTP_SSL(smtp_server, smtp_port) as server:
            server.login(smtp_user, smtp_pass)
            server.send_message(msg)
        return True
    except Exception as e:
        print(f"Error al enviar correo a {to_email}: {str(e)}")
        return False
