import asyncio
import os
import json
from datetime import datetime
from dotenv import load_dotenv

try:
    from telethon import TelegramClient, events, Button
except ImportError as e:
    print(f"ERROR CRITICO: Falta libreria {e}")
    exit(1)

load_dotenv()

API_ID = int(os.getenv('API_ID', 0))
API_HASH = os.getenv('API_HASH', '')
BOT_TOKEN = os.getenv('BOT_TOKEN', '')

if not all([API_ID, API_HASH, BOT_TOKEN]):
    print("FALTAN CREDENCIALES")
    exit(1)

print("Bot Apartamentos Ricaurte - Iniciando...")

client = TelegramClient('bot_session', API_ID, API_HASH)

INFO_APARTAMENTO = """
APARTAMENTO EN RICAURTE - CUNDINAMARCA

Ubicacion: A 5km de Girardot
2 Alcobas, 2 Banos, Balcon
Aire acondicionado, Parqueadero
Piscina, Jacuzzi, Canchas
Cerca de Piscilago
"""

def crear_boton_whatsapp():
    url = "https://api.whatsapp.com/send?phone=+573228940561&text=vengo%20de%20parte%20de%20Wilfer%20Rodriguez"
    return [[Button.url("Contactar WhatsApp", url)]]

@client.on(events.NewMessage)
async def handler(event):
    nombre = event.sender.first_name or "Amigo"
    mensaje = (event.message.text or "").strip().lower()
    
    if mensaje in ['/start', 'hola']:
        await event.respond(f"Hola {nombre}! Comandos: /info, /fotos, /tarifas", buttons=crear_boton_whatsapp())
    elif mensaje == '/info':
        await event.respond(INFO_APARTAMENTO, buttons=crear_boton_whatsapp())
    elif mensaje == '/fotos':
        await event.respond("Aqui las fotos:", buttons=crear_boton_whatsapp())
    elif mensaje == '/tarifas':
        await event.respond("Temporada Baja: $400.000 fin de semana", buttons=crear_boton_whatsapp())
    else:
        await event.respond("Usa /start, /info, /fotos o /tarifas", buttons=crear_boton_whatsapp())

async def main():
    await client.start(bot_token=BOT_TOKEN)
    print("Bot conectado y escuchando...")
    await client.run_until_disconnected()

if __name__ == "__main__":
    asyncio.run(main())
