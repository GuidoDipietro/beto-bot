from flask import Flask
from threading import Thread
import discord
from discord import Webhook, RequestsWebhookAdapter

WH_ID = 770078260779417650
with open("wh_key.txt", "r") as f:
    TOP_SECRET_WH_TOKEN = f.readline()
    TOP_SECRET_ROUTE = f.readline()

app = Flask('')

@app.route('/')
def main():
  return "Henlo bro"

@app.route(f'/{TOP_SECRET_ROUTE}/<msg>', methods=["GET"])
def send_error_code_by_GET(msg):
    errmsg = [
      "",
      "Código de error #1 - Error en el test\n\n",
      "Código de error #2 - Error de Valgrind (posible leak)\n\n",
      "Código de error #3 - Error en la compilación (ver logs en GitHub)"
    ]
    errcolour = [
      discord.Colour.light_gray(),
      discord.Colour.magenta(),
      discord.Colour.red(),
      discord.Colour.purple()
    ]
    errors = msg.split("&")[1:]
    
    webhook = Webhook.partial(WH_ID,TOP_SECRET_WH_TOKEN,adapter=RequestsWebhookAdapter())
    webhook.send("El reporte del tío Lucas:")

    for error in errors:
      errcode, *filenames = error.split("*")
      errcode = int(errcode)

      embedVar = discord.Embed(title = errmsg[errcode], colour = errcolour[errcode])
      for filename in filenames:
        embedVar.add_field(name="\u200b", value=filename)
      webhook.send(embed=embedVar)

    return {"response": "Done."}

def run():
  app.run(host="0.0.0.0", port=8080)

def keepalive():
  server = Thread(target=run)
  server.start()