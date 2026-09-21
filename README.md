# trip-trace-telegram-bot

Segunda vía para TripTrace, además de la app Android — un bot de Telegram que usa **Live Location** para el tracking en tiempo real, en vez de un foreground service propio. No reemplaza a `trip-trace-android-app`; es una alternativa más liviana para validar el loop completo (crear → trackear → sync → ver resultado) sin depender de compilar nada pesado.

Le pega a la misma API (`trip-trace-api`) que usa la app.

## Cómo funciona

- `/nuevo_viaje <destino>` — pide que compartas tu ubicación actual (como origen) y crea el viaje
- `/iniciar` — marca el viaje como en curso. A partir de ahí, compartí tu **Ubicación en tiempo real** (clip 📎 > Ubicación > Compartir ubicación en tiempo real) — cada actualización que llegue se sube como punto GPS
- `/finalizar` — termina el viaje, calcula y devuelve las métricas (distancia, velocidad)

El bot no puede activar el compartir ubicación por sí solo — es una limitación de la API de Telegram, tenés que iniciarlo vos manualmente desde el clip de adjuntos después de `/iniciar`.

## Setup

1. Hablá con [@BotFather](https://t.me/BotFather) en Telegram, `/newbot`, seguí los pasos, guardá el token.
2. Necesitás tu `user_id` de Telegram (por ejemplo, hablando con [@userinfobot](https://t.me/userinfobot)) — el bot solo responde a ese usuario.
3. Copiá `.env.default` a `.env` y completá los valores.
4. `chmod +x start.sh` (una sola vez — GitHub no preserva el bit ejecutable al clonar).
5. `./start.sh` — crea el entorno virtual si no existe, instala/actualiza dependencias, y corre el bot.

Corre por polling — no necesita URL pública ni HTTPS, sirve para correrlo local.
