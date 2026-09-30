# trip-trace-telegram-bot

Bot de Telegram para TripTrace. Es otro frontend, igual que el web: sirve para **consultar** viajes y
estadísticas desde un chat y, más adelante, para programar viajes. **No inicia ni finaliza viajes**; eso
se hace desde la app Android.

Le pega a la misma API (`trip-trace-api`) que usan la app y el frontend web.

## Comandos

| Comando   | Qué hace                                             |
| --------- | ---------------------------------------------------- |
| `/ayuda`  | Lista los comandos (`/start` hace lo mismo)          |
| `/estado` | Verifica la conexión con la API y con qué cuenta     |

Lo que viene está en los issues: ver viajes (#4), estadísticas (#5), programar viajes (#6) y dónde
correrlo (#7).

## Estructura

```
trip_trace_bot/
├── __main__.py        # entrada: python -m trip_trace_bot
├── config.py          # lee y valida las variables de entorno
├── api/
│   └── client.py      # cliente HTTP de trip-trace-api (login, token, reintento ante 401)
└── bot/
    ├── app.py         # arma la Application de python-telegram-bot y registra los handlers
    ├── context.py     # acceso tipado a lo compartido entre handlers (el cliente de la API)
    ├── errors.py      # handler global de errores: loguea y responde en castellano
    ├── messages.py    # todos los textos que ve el usuario
    └── handlers/      # un módulo por funcionalidad, cada uno con register()
        ├── help.py
        └── status.py
tests/                 # pytest, sin Telegram ni API reales
```

Para agregar un comando nuevo: crear un módulo en `bot/handlers/` con su `register(application, allowed)`,
sumarlo a `MODULES` en `bot/handlers/__init__.py` y, si va en el menú de Telegram, a `COMMANDS` en
`bot/app.py`. Las llamadas a la API van en `api/client.py`, nunca directo desde un handler.

## Setup

1. Hablá con [@BotFather](https://t.me/BotFather) en Telegram, `/newbot`, y guardá el token.
2. Conseguí tu `user_id` de Telegram (por ejemplo, con [@userinfobot](https://t.me/userinfobot)). El bot
   solo responde a los ids de `ALLOWED_TELEGRAM_USER_IDS`; al resto lo ignora y lo deja en el log.
3. `cp .env.default .env` y completá los valores.
4. `bash start.sh` (crea el venv si falta, instala dependencias y corre el bot).

Corre por polling: no necesita URL pública ni HTTPS.

## Configuración

| Variable                    | Default                               | Descripción                                   |
| --------------------------- | ------------------------------------- | --------------------------------------------- |
| `TELEGRAM_BOT_TOKEN`        | (obligatoria)                         | Token de @BotFather                           |
| `ALLOWED_TELEGRAM_USER_IDS` | (obligatoria)                         | Ids de Telegram separados por coma            |
| `API_URL`                   | `https://trip-trace-api.onrender.com` | URL base de trip-trace-api                    |
| `API_USERNAME`              | (obligatoria)                         | Email o usuario de la cuenta de TripTrace     |
| `API_PASSWORD`              | (obligatoria)                         | Contraseña de esa cuenta                      |
| `API_TIMEOUT_SECONDS`       | `30`                                  | Timeout de cada request a la API              |
| `LOG_LEVEL`                 | `INFO`                                | `DEBUG`, `INFO`, `WARNING`, `ERROR`           |

`.env` y `.env.prod` están en `.gitignore`. Con `APP_ENV=prod` se lee `.env.prod` en vez de `.env`.

## Desarrollo

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements-dev.txt
.venv/bin/ruff check . && .venv/bin/ruff format --check .
.venv/bin/pytest
```
