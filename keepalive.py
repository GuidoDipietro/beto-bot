from flask import Flask
from threading import Thread
from discord import Webhook, RequestsWebhookAdapter

WH_ID = 770078260779417650
with open("wh_key.txt", "r") as f:
    TOP_SECRET_WH_TOKEN = f.readline()
    TOP_SECRET_ROUTE = f.readline()

app = Flask('')

@app.route('/')
def main():
  return "Henlo bro"

@app.route(f'/{TOP_SECRET_ROUTE}/<msg>', methods=["POST", "GET"])
def send_msg_by_POST(msg):
    webhook = Webhook.partial(WH_ID,TOP_SECRET_WH_TOKEN,adapter=RequestsWebhookAdapter())
    webhook.send("*Enviado mediante un POST request. ¡No me hago responsable del contenido!*")
    webhook.send(msg)
    return {"response": "Just sent {msg}."}

def run():
  app.run(host="0.0.0.0", port=8080)

def keepalive():
  server = Thread(target=run)
  server.start()