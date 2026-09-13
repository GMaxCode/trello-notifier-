from fastapi import FastAPI
from fastapi.responses import JSONResponse
from fastapi import Request 


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

        print(f"Novo card: {card_name}")
        print(f"Lista: {list_name}")
        print(f"Criado por: {member_name}")

    return JSONResponse(content={"received": True}, status_code=200)