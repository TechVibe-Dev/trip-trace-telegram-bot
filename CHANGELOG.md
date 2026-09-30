# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/), and this project adheres
to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- Bot skeleton as a read-only TripTrace front-end on `python-telegram-bot` 22.8: `trip_trace_bot` package split into config, API client and Telegram handlers (one module per feature), `/start`, `/ayuda` and `/estado` commands, Telegram command menu, access restricted to `ALLOWED_TELEGRAM_USER_IDS`, a global error handler with Spanish replies, and `start.sh`. The API client logs in once and only logs in again on a 401, since `/auth/login` is rate limited. Replaces the Live Location tracking prototype, which was never merged. Includes pytest tests. Part of #3. ([#8](https://github.com/TechVibe-Dev/trip-trace-telegram-bot/pull/8))
