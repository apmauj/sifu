# Scheduler Business Day Logic

Added on 2025-08-18.

The automatic refresh jobs for UI and Exchange Rates now skip non-business days by default.

Rules:

- Business day = Monday to Friday (UTC) and not listed in `SCHEDULER_HOLIDAYS`.
- Environment variable `SCHEDULER_BUSINESS_DAY_ONLY` (default `true`). Set to `false` to run every scheduled day regardless of weekday/holiday.
- Holidays: set `SCHEDULER_HOLIDAYS=2025-01-01,2025-05-01` (comma separated ISO dates) to skip those days.
- UR monthly refresh does NOT skip weekends (runs as scheduled) because monthly data often published on first calendar day; adjust if needed.

Environment variables summary:

- `SCHEDULE_UI_REFRESH_CRON` (default `0 2 * * *`)
- `SCHEDULE_EXCHANGE_REFRESH_CRON` (default `0 3 * * *`)
- `SCHEDULE_UR_REFRESH_CRON` (default `0 4 1 * *`)
- `SCHEDULER_BUSINESS_DAY_ONLY` (default `true`)
- `SCHEDULER_HOLIDAYS` (comma separated ISO dates)

If you need locale-specific business days (e.g., Uruguay time), set `SCHEDULER_TIMEZONE` accordingly so cron triggers fire in that zone; the weekday calculation still uses UTC clock inside `_is_business_day()`—modify to use that timezone if strict local-day classification is required.
