import asyncio
import os
import json
from datetime import datetime
from dotenv import load_dotenv

try:
    from telethon import TelegramClient, events
    from telethon.tl.types import KeyboardButton, ReplyKeyboardMarkup
except ImportError as e:
    print(f"❌ ERROR CRÍTICO: Falta librería {e}")
    exit(1)

load_dotenv()

# === CONFIGURACIÓN ===
API_ID = int(os.getenv('API_ID', 0))
API_HASH = os.getenv('API_HASH', '')
BOT_TOKEN = os.getenv('BOT_TOKEN', '')

DB_FILE = "clientes.json"

if not all([API_ID, API_HASH, BOT_TOKEN]):
    print("❌ FALTAN CREDENCIALES (API_ID, API_HASH o BOT_TOKEN)")
    exit(1)

print("🏖️ Bot Apartamentos Ricaurte - Iniciando...")

# Inicializamos el cliente (sin .start() aquí, lo haremos en main())
client = TelegramClient('bot_session', API_ID, API_HASH)

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
"""

# === BASE DE DATOS ===
def cargar_db():
    if os.path.exists(DB_FILE):
        try:
            with open(DB_FILE, 'r') as f:
                return json.load(f)
        except Exception:
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
                await asyncio.sleep(1.5)  # Pausa un poco más larga para evitar límites de Telegram
            except Exception as e:
                print(f"⚠️ Error enviando {img_path}: {e}")
        else:
            print(f"⚠️ Imagen no encontrada: {img_path}")
            
    await event.respond("📱 **¿Te gustó?** Escríbenos al WhatsApp para reservar.", buttons=crear_teclado_whatsapp())

# === BOTÓN DE WHATSAPP ===
def crear_teclado_whatsapp():
    url = "https://api.whatsapp.com/send?phone=+573228940561&text=vengo%20de%20parte%20de%20Wilfer%20Rodriguez,%20ya%20decid%C3%AD%20vacacionar"
    return ReplyKeyboardMarkup([[KeyboardButton('📱 Contactar por WhatsApp', url=url)]], resize=True)

# === HANDLER DE MENSAJES (SOLO REACTIVO) ===
@client.on(events.NewMessage)
async def handler(event):
    # Ignorar mensajes enviados por el mismo bot
    me = await client.get_me()
    if event.sender_id == me.id:
        return
    
    nombre = event.sender.first_name or "Amigo"
    username = event.sender.username or "Sin username"
    mensaje = (event.message.text or "").strip().lower()
    
    # Registrar automáticamente en la base de datos
    registrar_cliente(event.sender_id, nombre, username)
    
    if mensaje in ['/start', 'hola', 'buenas', 'inicio', '']:
        await event.respond(
            f"👋 ¡Hola {nombre}! Bienvenido a **Arte Diverso - Apartamentos**\n\n"
            f"📌 **Comandos disponibles:**\n"
            f"• /info - Detalles del apartamento\n"
            f"• /fotos - Ver galería completa\n"
            f"• /tarifas - Precios y promociones\n"
            f"• /disponibilidad - Fechas libres\n"
            f"• /ubicacion - Ubicación y turismo\n"
            f"• /contacto - Hablar con admin", 
            buttons=crear_teclado_whatsapp()
        )
    
    elif mensaje in ['/info', 'informacion', 'información', 'detalles']:
        await event.respond(INFO_APARTAMENTO, parse_mode='markdown', buttons=crear_teclado_whatsapp())
    
    elif mensaje in ['/fotos', 'imagenes', 'imágenes', 'galeria']:
        await enviar_galeria(event)
    
    elif mensaje in ['/tarifas', 'precios', 'valor', 'cuanto', 'cuánto']:
        await event.respond(
            "💰 **TARIFAS APARTAMENTO RICAURTE**\n\n"
            "**Temporada Baja:**\n"
            "• Fin de semana: $400.000 COP\n"
            "• Semana completa: $900.000 COP\n\n"
            "**Temporada Alta:**\n"
            "• Fin de semana: $550.000 COP\n"
            "• Semana completa: $1'200.000 COP\n\n"
            "✅ **Incluye:** Piscina, parqueadero, agua y luz.\n"
            "❌ **No incluye:** Ropa de cama ($30.000) ni aseo final ($50.000).", 
            buttons=crear_teclado_whatsapp()
        )
    
    elif mensaje in ['/disponibilidad', 'disponible', 'fechas', 'cuando']:
        await event.respond(
            "📅 **CONSULTA DE DISPONIBILIDAD**\n\n"
            "Para verificar fechas, indícame:\n"
            "1️⃣ ¿Cuántas personas van?\n"
            "2️⃣ ¿Qué fechas te interesan? (mes y día)\n"
            "3️⃣ ¿Cuántas noches necesitas?\n\n"
            "Te respondo en menos de 1 hora 😊", 
            buttons=crear_teclado_whatsapp()
        )
    
    elif mensaje in ['/ubicacion', 'donde', 'ubicación', 'sitios', 'turismo']:
        await event.respond(
            "📍 **UBICACIÓN Y ALREDEDORES**\n"
            "Ricaurte, Cundinamarca (5km de Girardot, 1 cuadra del parque).\n\n"
            "**Cerca de:**\n"
            "• Piscilago (15 min)\n"
            "• Humedal el Yulo (10 min)\n"
            "• Inflaparque Ikarus (20 min)\n"
            "• Xielo Skydive (25 min)", 
            buttons=crear_teclado_whatsapp()
        )
    
    elif mensaje in ['/contacto', 'admin', 'administrador', 'humano', 'whatsapp']:
        await event.respond(
            "👤 **CONTACTO DIRECTO**\n"
            "📱 WhatsApp: +57 322 894 0561\n"
            "👤 Wilfer Rodriguez\n"
            "🎬 TikTok: @melen6019", 
            buttons=crear_teclado_whatsapp()
        )
    
    else:
        await event.respond(
            f"Gracias por escribir, {nombre} 👋\n"
            f"Usa /info, /fotos o /tarifas, o haz clic en el botón de WhatsApp abajo.", 
            buttons=crear_teclado_whatsapp()
        )

# === INICIO ===
async def main():
    # Iniciamos el bot de forma segura dentro del bucle de eventos
    await client.start(bot_token=BOT_TOKEN)
    print("✅ Bot conectado y escuchando mensajes...")
    print("📊 Base de datos activa: clientes.json")
    
    try:
        await client.run_until_disconnected()
    except Exception as e:
        print(f"❌ Error en la conexión: {e}")

if __name__ == "__main__":
    asyncio.run(main())
