from flask import Flask
from threading import Thread
import time

app = Flask(__name__)

@app.route('/')
def home():
    return "Le bot est en ligne !"

def run():
    """Démarre le serveur Flask."""
    app.run(host='0.0.0.0', port=8080)

def prevent_sleep():
    """Boucle qui tourne en permanence pour éviter la mise en veille de Render."""
    while True:
        time.sleep(180)  # ⏳ Attente de 3 minutes (180 secondes)
        print("🔄 Garder Render actif...")

def keep_alive():
    """Démarrer Flask et la boucle anti-sleep en parallèle."""
    t1 = Thread(target=run)
    t2 = Thread(target=prevent_sleep)
    t1.start()
    t2.start()
