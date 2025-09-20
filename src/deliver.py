import smtplib, ssl
from email.mime.text import MIMEText

# Add other options: telegram, teams, slack, ...

def send_email(html: str, subject: str, to_addr: str, from_addr: str, smtp_host: str, smtp_port: int, username: str, password: str):
    msg = MIMEText(html, "html")
    msg["Subject"] = subject
    msg["From"] = from_addr
    msg["To"] = to_addr
    ctx = ssl.create_default_context()
    with smtplib.SMTP_SSL(smtp_host, smtp_port, context=ctx) as s:
        s.login(username, password)
        s.sendmail(from_addr, [to_addr], msg.as_string())
