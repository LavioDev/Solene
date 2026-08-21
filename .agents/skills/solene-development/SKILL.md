---
name: solene-development
description: Standards, conventions, and architectural guidelines for developing the Solène platform across Backend (Python 3.12 Clean Architecture) and Frontend (Vue 3 TypeScript Minimalist Pastel Native UI).
---

# Solène Project Development Skill & Conventions Guide

This document establishes setup standards, architectural rules, Clean Code guidelines, and UI design conventions for the **Solène** project. All developers and AI Agents working on this codebase must strictly adhere to these rules.

---

## 1. GLOBAL CRITICAL CONVENTIONS

### 1.1 PROJECT NAME & IDENTITY
- The project is named strictly **Solène** (with accent `è`).
- Do NOT use redundant extensions like "Solène IoT", "Solene IoT", "Solène AI", "Solene AI", or "Industrial Machine State Server".

### 1.2 MULTI-LANGUAGE I18N STANDARDS
- Multi-language support is mandatory across the entire application using `vue-i18n`.
- Default Language: **English (`en`)**.
- Supported Languages:
  - **English (`en`)** [Default]
  - **Vietnamese (`vi`)**
  - **French (`fr`)**
  - **Chinese (`zh`)**
- Language switching is managed dynamically via `AppLangSwitcher.vue` and persisted in `localStorage` under key `'solene_language'`.
- All user-facing labels, headings, buttons, and placeholders MUST use translation keys (`$t('key')` or `t('key')`). Never hardcode text strings directly in templates.

### 1.3 NO MANUAL RESOLVE FUNCTIONS & NO STRING CONCATENATION FOR PATHS OR URLS
- Absolutely prohibited to use string concatenation (`+`) to build file paths, URLs, query parameters, or dynamic strings.

---

## 2. BACKEND CODE STANDARDS (PYTHON 3.12 + FASTAPI)

### 2.1 Architecture & Design Patterns
- Modular Monolith with Clean Architecture (`models.py`, `schemas.py`, `repository.py`, `service.py`).
- Rule-Based Events Engine: Store 1 single rule in DB per recurring event (`EVERY_N_DAYS`, `MONTHLY`, `YEARLY`, `SINGLE`).

---

## 3. FRONTEND CODE STANDARDS (VUE 3 + TAILWIND CSS + TYPESCRIPT)

### 3.1 UI/UX Style: Strict Native UI Component Library
- Minimalist, white-dominant background (`#ffffff` / `#fafafa`) with violet accents (`#7c3aed` / `#6d28d9`), rounded corners (`rounded-xl`), and soft shadows (`shadow-2xs` / `shadow-card`).
- MANDATORY Native UI Component Primitives:
  - `AppButton.vue`: Native UI styled buttons.
  - `AppInput.vue`: Native UI styled text/number/date inputs.
  - `AppSelect.vue`: Custom styled native select dropdown (`appearance-none` with custom `ChevronDown` arrow). Never use raw unstyled browser `<select>`.
  - `AppTextarea.vue`: Custom styled native textarea (`rounded-xl`, violet focus ring). Never use raw unstyled browser `<textarea>`.
  - `AppModal.vue`: Glassmorphism modal with Vue `<Transition>` animations (backdrop fade + scale zoom transform).
  - `AppConfirmModal.vue`: Native UI confirm modal dialogs for deletion/warning actions. Never use raw browser `confirm()` or `alert()`.
  - `AppLangSwitcher.vue`: Multi-language selector (EN, VI, FR, ZH).

### 3.2 Width Presets
- Fixed min-width options `800px` (default), `1000px`, `1200px` hardcoded per component layout requirement.
