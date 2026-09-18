import asyncio
import os
import json
from datetime import datetime
from dotenv import load_dotenv

try:
    from telethon import TelegramClient, events
    from telethon.sessions import StringSession
    from telethon.tl.types import KeyboardButton, ReplyKeyboardMarkup
except ImportError as e:
    print(f"❌ ERROR CRÍTICO: Falta librería {e}")
    exit(1)

load_dotenv()

# === CONFIGURACIÓN ===
API_ID = int(os.getenv('API_ID', 0))
API_HASH = os.getenv('API_HASH', '')
SESSION_STRING = os.getenv('SESSION_STRING', '')

DB_FILE = "clientes.json"

if not all([API_ID, API_HASH]):
    print("❌ FALTAN CREDENCIALES DE TELEGRAM")
    exit(1)

print("🏖️ Bot Apartamentos Ricaurte - Iniciando (Modo Reactivo)...")
client = TelegramClient(StringSession(SESSION_STRING), API_ID, API_HASH)

# === INFORMACIÓN DEL APARTAMENTO ===
INFO_APARTAMENTO = """
🏖️ **APARTAMENTO EN RICAURTE - CUNDINAMARCA**

📍 **Ubicación:**
• A 5km de Girardot
• 1 cuadra del parque principal
• Piso 6 con vista privilegiada

🛏️ **Características:**
• 2 Alcobas amplias
• 2 Baños completos
• Balcón con vista
• Aire acondicionado
• Parqueadero privado

🏊 **Zona Comunal:**
• Piscina adultos y niños
• Jacuzzi
• Cancha de vóley playa
• Fútbol (césped sintético)
• Baloncesto

🎯 **Sitios Turísticos Cercanos:**
• Piscilago (15 min)
• Humedal el Yulo
• Inflaparque Acuático Ikarus
• Xielo Skydive

💰 **Tarifas:** Consultar por DM
📅 **Disponibilidad:** Consultar calendario

*¡Perfecto para familias y grupos!*
"""

# === BASE DE DATOS ===
def cargar_db():
    if os.path.exists(DB_FILE):
        try:
            with open(DB_FILE, 'r') as f:
                return json.load(f)
        except:
            return {"clientes": []}
    return {"clientes": []}

def guardar_db(data):
    with open(DB_FILE, 'w') as f:
        json.dump(data, f, indent=2)

def registrar_cliente(telegram_id, nombre, username):
    db = cargar_db()
    for cliente in db["clientes"]:
        if cliente["telegram_id"] == telegram_id:
            return False  # Ya existe
    
    db["clientes"].append({
        "telegram_id": telegram_id,
        "nombre": nombre,
        "username": username,
        "fecha_registro": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    })
    guardar_db(db)
    print(f"✅ Cliente registrado en DB: {nombre} (@{username})")
    return True

# === ENVIAR IMÁGENES ===
async def enviar_galeria(event):
    imagenes = [
        "img/apto_dentro.jpeg",
        "img/apto_dentro2.jpeg",
        "img/aptos_vacacional.jpeg",
        "img/cocina_vacacional.jpeg",
        "img/pieza_vacacional.jpeg",
        "img/piscina_vacacional.jpeg",
        "img/publicidad_vacacional.jpeg"
    ]
    
    await event.respond("📸 **Aquí te comparto la galería del apartamento:**")
    
    for img_path in imagenes:
        if os.path.exists(img_path):
            try:
                await event.respond(file=img_path)
                await asyncio.sleep(1)
            except Exception as e:
                print(f"⚠️ Error enviando {img_path}: {e}")
    
    await event.respond("📱 **¿Te gustó?** Escríbenos al WhatsApp para reservar.", buttons=crear_teclado_whatsapp())

# === BOTÓN DE WHATSAPP ===
def crear_teclado_whatsapp():
    url = "https://api.whatsapp.com/send?phone=+573228940561&text=vengo%20de%20parte%20de%20Wilfer%20Rodriguez,%20ya%20decid%C3%AD%20vacacionar"
    return ReplyKeyboardMarkup([[KeyboardButton('📱 Contactar por WhatsApp', url=url)]], resize=True)

# === HANDLER DE MENSAJES (SOLO REACTIVO) ===
@client.on(events.NewMessage)
async def handler(event):
    if event.sender_id == (await client.get_me()).id:
        return
    
    nombre = event.sender.first_name or "Amigo"
    username = event.sender.username or "Sin username"
    mensaje = (event.message.text or "").strip().lower()
    
    # Registrar automáticamente en la base de datos
    registrar_cliente(event.sender_id, nombre, username)
    
    if mensaje in ['/start', '/inicio', 'hola', 'buenas', '']:
        await event.respond(f"👋 ¡Hola {nombre}! Bienvenido a **Arte Diverso - Apartamentos**\n\n📌 **Comandos:**\n• /info - Detalles\n• /fotos - Galería\n• /tarifas - Precios\n• /disponibilidad - Fechas\n• /ubicacion - Turismo\n• /contacto - Admin", buttons=crear_teclado_whatsapp())
    
    elif mensaje in ['/info', 'informacion', 'detalles']:
        await event.respond(INFO_APARTAMENTO, parse_mode='markdown', buttons=crear_teclado_whatsapp())
    
    elif mensaje in ['/fotos', 'imagenes', 'galeria']:
        await enviar_galeria(event)
    
    elif mensaje in ['/tarifas', 'precios', 'valor']:
        await event.respond("💰 **TARIFAS**\n\n**Temporada Baja:**\n• Fin de semana: $400.000 COP\n• Semana: $900.000 COP\n\n**Temporada Alta:**\n• Fin de semana: $550.000 COP\n• Semana: $1'200.000 COP\n\n✅ Incluye: Piscina, parqueadero, agua y luz.\n❌ No incluye: Ropa de cama ($30.000) ni aseo final ($50.000).", buttons=crear_teclado_whatsapp())
    
    elif mensaje in ['/disponibilidad', 'fechas']:
        await event.respond("📅 **CONSULTA DE DISPONIBILIDAD**\n\nPara verificar fechas, indícame:\n1️⃣ ¿Cuántas personas van?\n2️⃣ ¿Qué fechas te interesan?\n3️⃣ ¿Cuántas noches necesitas?", buttons=crear_teclado_whatsapp())
    
    elif mensaje in ['/ubicacion', 'turismo']:
        await event.respond("📍 **UBICACIÓN**\nRicaurte, Cundinamarca (5km de Girardot, 1 cuadra del parque).\n\n**Cerca de:**\n• Piscilago (15 min)\n• Humedal el Yulo (10 min)\n• Inflaparque Ikarus (20 min)\n• Xielo Skydive (25 min)", buttons=crear_teclado_whatsapp())
    
    elif mensaje in ['/contacto', 'admin', 'whatsapp']:
        await event.respond("👤 **CONTACTO DIRECTO**\n📱 WhatsApp: +57 322 894 0561\n👤 Wilfer Rodriguez\n🎬 TikTok: @melen6019", buttons=crear_teclado_whatsapp())
    
    else:
        await event.respond(f"Gracias por escribir, {nombre} 👋\nUsa /info, /fotos o /tarifas, o haz clic en el botón de WhatsApp.", buttons=crear_teclado_whatsapp())

# === INICIO ===
async def main():
    await client.start()
    print("✅ Bot conectado. Solo atenderá a quien le escriba.")
    print("📊 Base de datos activa: clientes.json")
    await client.run_until_disconnected()

if __name__ == "__main__":
    asyncio.run(main())
       # Forzar actualizacion Northflank
