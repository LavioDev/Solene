# Solène

Solène is an intelligent, multi-modal robot platform built with Clean Architecture. The platform connects ESP32-S3 edge hardware nodes with a high-performance Python 3.12 FastAPI backend and an elegant Vue 3 TypeScript Single Page Application (SPA).

Solène incorporates multi-modal perception and interaction capabilities:
- Vision Perception: Receives direct image streams from an OV3660 camera, processed through Computer Vision models with real-time feedback.
- Voice Interaction: Full-duplex conversational pipeline with Voice Activity Detection (VAD), Speech-to-Text (STT), AI Agent context processing, and natural Speech Synthesis (TTS).
- Visual Display: Media transcoding and streaming engine pushing video and graphical representations onto an SPI TFT display.
- Core Device & Memory Management: Real-time telemetry ingestion, special events & anniversary tracking rules, device management, and remote configuration.

---

## 1. Specification & Architecture Documentation

Detailed system specifications and architectural designs are available in the `docs/` directory:

- [01. System Specification](docs/01_SYSTEM_SPECIFICATION.md): Hardware specs and functional/non-functional requirements.
- [02. System Architecture Design](docs/02_ARCHITECTURE_DESIGN.md): End-to-End topology diagrams, communication protocol matrix (MQTT, WebSocket, REST), and PostgreSQL database ERD.
- [03. Project Structure](docs/03_PROJECT_STRUCTURE.md): Monorepo structure, backend domain module layout (vision, voice, display, devices, events), and feature-based Vue 3 frontend organization.

---

## 2. High-Level Architecture Overview

```
+-------------------------------------------------------------------+
|                           SOLÈNE ROBOT                            |
|   [OV3660 Camera]       [I2S Mic & Speaker]     [ST7789 Display]  |
+---------------------------------+---------------------------------+
                                  |
              (WebSockets Full-Duplex / MQTT v5 / TLS)
                                  |
                                  v
+-------------------------------------------------------------------+
|                  FASTAPI BACKEND (PYTHON 3.12)                    |
|   - Async WebSocket Hub (High Concurrency)                        |
|   - Modular Domain Services: vision, voice, display, devices, events|
|   - Zero-Lag Frame Sampler & Transcoding Engine                   |
+---------------------------------+---------------------------------+
                                  |
            +---------------------+---------------------+
            |                                           |
            v                                           v
+-----------------------------+             +-----------------------------+
|     AI & MEDIA ENGINES      |             |   PERSISTENCE & CACHE       |
| - Computer Vision (YOLO)    |             | - PostgreSQL 16 (Relational)|
| - Faster-Whisper + Piper TTS|             | - Redis (Cache & Pub/Sub)   |
| - LLM Agent Routing Engine  |             | - MinIO / S3 (Media & OTA)  |
| - FFmpeg Video Transcoder   |             +-----------------------------+
+-----------------------------+
```

---

## 3. Quick Start

### Backend (Port 8200)
```powershell
cd backend
python -m uvicorn app.main:app --host 0.0.0.0 --port 8200 --reload
```

### Frontend (Port 5173)
```powershell
cd frontend
npm run dev
```
