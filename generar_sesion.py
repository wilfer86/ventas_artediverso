from telethon import TelegramClient
import asyncio

# Tus credenciales de Telegram (my.telegram.org)
API_ID = 34566164
API_HASH = 'dcfb2cb9e5cad0625c152436a5db7a8a'
PHONE = '+573171547065'

async def main():
    print("🔑 Iniciando sesión de Telegram...")
    print("📱 Se enviará un código a tu número")
    
    # Crear cliente con el nombre 'sesion' (esto creará sesion.session)
    client = TelegramClient('sesion', API_ID, API_HASH)
    
    # Iniciar sesión (pedirá el código automáticamente)
    await client.start(phone=PHONE)
    
    print("✅ ¡ÉXITO! Archivo 'sesion.session' creado")
    print("📁 Ahora debes descargar/subir este archivo a GitHub")
    
    await client.disconnect()

if __name__ == '__main__':
    asyncio.run(main())
