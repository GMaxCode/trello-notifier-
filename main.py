from fastapi import FastAPI
from fastapi.responses import JSONResponse
from fastapi import Request
import os
from dotenv import load_dotenv
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

load_dotenv()

GMAIL_USER = os.environ.get("GMAIL_USER")
GMAIL_APP_PASSWORD = os.environ.get("GMAIL_APP_PASSWORD")
RECIPIENT_EMAILS = os.environ.get("RECIPIENT_EMAILS", "")



def send_email_notification(subject: str, body: str) -> None:
    recipients = [email.strip() for email in RECIPIENT_EMAILS.split(",") if email.strip()]

    if not recipients:
        print("Nenhum destinatário configurado, e-mail não enviado.")
        return

    msg = MIMEMultipart()
    msg["From"] = GMAIL_USER
    msg["To"] = ", ".join(recipients)
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "plain"))

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(GMAIL_USER, GMAIL_APP_PASSWORD)
        server.sendmail(GMAIL_USER, recipients, msg.as_string())

    print(f"E-mail enviado para: {recipients}")

app = FastAPI()

@app.get("/")
def health_check():
    return {'status': 'ok', 'message': 'Trello Notifier está rodando'}


@app.head('/webhook/trello')
def trello_webhook_verification(): 
    return JSONResponse(content=None, status_code=200)


@app.post('/webhook/trello')
async def trello_webhook(request: Request):
    payload = await request.json()

    action = payload.get("action", {})
    action_type = action.get("type")

    if action_type == "createCard":
        card_name = action.get("data", {}).get("card", {}).get("name", "sem título")
        list_name = action.get("data", {}).get("list", {}).get("name", "lista desconhecida")
        member_name = action.get("memberCreator", {}).get("fullName", "alguém")

        subject = f'nova demanda no Trello: {card_name}'
        body =(
        f"Um novo card foi criado no Trello: \n\n"
        f"Card: {card_name}\n"
        f"Lista: {list_name}\n"
        f"Criado por: {member_name}\n"
        )

        send_email_notification(subject, body)


    return JSONResponse(content={"received": True}, status_code=200) 