# Solène Project Development Rules & Constraints

## 1. PROJECT NAME & IDENTITY
- The project name is strictly **Solène** (with accent `è`).

## 2. CODE & UI CONVENTIONS (ALWAYS ON)
- Multi-Language i18n:
  - vue-i18n is mandatory. Default language: **English (`en`)**.
  - Supported locales: `en` (English), `vi` (Vietnamese), `fr` (French), `zh` (Chinese).
  - All user-facing strings must use translation keys via `$t` or `t()`.
  - Language selection persisted in `localStorage`.
- NO string concatenation (`+`) or `resolve()` for paths/URLs.
- Backend: Clean Architecture (`app/modules/<domain>/`). Rule-based recurring events engine (`EVERY_N_DAYS`, `MONTHLY`, `YEARLY`, `SINGLE`).
- Frontend Component Primitives:
  - MANDATORY use of Native UI components: `AppButton`, `AppInput`, `AppSelect`, `AppTextarea`, `AppModal`, `AppConfirmModal`, `AppLangSwitcher`, `AppCard`, `AppBadge`.
  - NEVER use raw browser `<select>`, raw `<textarea>`, browser `confirm()`, or browser `alert()`.
- Layout Width Presets: Fixed min-width options `800px` (default), `1000px`, `1200px` hardcoded per component requirement.
- Modals: Vue `<Transition>` animations (backdrop fade + scale zoom).
