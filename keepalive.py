from flask import Flask
from threading import Thread

app = Flask('')

@app.route('/')
def main():
  return "Henlo bro"

def run():
  app.run(host="0.0.0.0", port=8080)

def keepalive():
  server = Thread(target=run)
  server.start()