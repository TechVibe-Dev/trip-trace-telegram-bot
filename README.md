# trip-trace-telegram-bot

Bot de Telegram para [TripTrace](https://github.com/TechVibe-Dev/trip-trace-android-app) — una segunda vía para crear, iniciar y finalizar viajes, usando la función **Live Location** de Telegram para el tracking de GPS. No reemplaza a la app Android, es una alternativa más liviana para probar el loop completo (crear → trackear → sync → ver resultado) rápido, sin depender de compilar nada localmente.

Le pega directo a [`trip-trace-api`](https://github.com/TechVibe-Dev/trip-trace-api) — mismos endpoints que usa la app.

## Cómo funciona

- `/nuevo_viaje <destino>` — pide compartir tu ubicación actual (una sola vez) para usarla como origen del viaje.
- `/iniciar` — marca el viaje como en curso. A partir de acá, compartí tu **Ubicación en tiempo real** (clip 📎 → Ubicación → Compartir ubicación en tiempo real) — cada actualización que llegue se sube como un punto GPS.
- `/finalizar` — marca el viaje como completado y calcula las métricas finales (distancia, velocidad).

**Nota:** Telegram no deja que un bot active el compartir ubicación por su cuenta — el usuario tiene que hacerlo a mano desde el clip de adjuntos, cada vez.

## Setup local

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.default .env
# completar .env con tu token de bot y credenciales
python bot.py
```

### Conseguir el token del bot

Hablá con [@BotFather](https://t.me/BotFather) en Telegram, `/newbot`, seguí los pasos, y te da el token para `TELEGRAM_BOT_TOKEN`.

### Conseguir tu ID de Telegram

Hablá con [@userinfobot](https://t.me/userinfobot) — te devuelve tu `ALLOWED_TELEGRAM_USER_ID`. Es un control de acceso básico: el bot ignora a cualquiera que no sea ese ID.
