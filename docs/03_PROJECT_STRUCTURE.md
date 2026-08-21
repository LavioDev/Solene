# PROJECT DIRECTORY & CODEBASE STRUCTURE
## PROJECT: SOLENE IOT SMART HUB & AI PLATFORM

---

## 1. MONOREPO STRUCTURE

```text
Solene/
├── .github/                     # CI/CD Workflows (Lint, Test, Docker Build)
├── .agents/                     # Antigravity Agent skills & rule conventions
│   ├── rules/
│   │   └── solene-conventions.md
│   └── skills/
│       └── solene-development/
│           └── SKILL.md
├── docs/                        # Specifications, architecture, & API docs
│   ├── 01_SYSTEM_SPECIFICATION.md
│   ├── 02_ARCHITECTURE_DESIGN.md
│   └── 03_PROJECT_STRUCTURE.md
├── backend/                     # Python 3.12 + FastAPI Core
├── frontend/                    # Vue 3 + Tailwind CSS + Pinia SPA
├── firmware/                    # ESP32-S3 Firmware (ESP-IDF / PlatformIO C++)
├── docker-compose.yml           # Dev & Local testing environment
├── docker-compose.prod.yml      # Production stack orchestration
└── README.md                    # Overview & setup guide
```

---

## 2. BACKEND DIRECTORY STRUCTURE (PYTHON 3.12 + FASTAPI)

The backend is organized as a Domain-Driven Modular Monolith, where hardware capabilities and major feature areas are isolated into independent domain modules containing Models, Schemas, Repositories, Services, and Controllers.

```text
backend/
├── alembic/                          # Database Migrations
│   ├── versions/
│   └── env.py
│
├── app/
│   ├── api/                          # HTTP REST API & WebSocket Routers
│   │   ├── deps.py                   # Dependency Injections (Auth, DB Session, Device Key)
│   │   ├── v1/
│   │   │   ├── router.py             # Root router v1 aggregation
│   │   │   ├── auth_router.py        # Authentication & JWT refresh
│   │   │   ├── user_router.py        # User management & RBAC
│   │   │   ├── device_router.py      # Device CRUD, pairing, & config
│   │   │   ├── ota_router.py         # Firmware upload & distribution
│   │   │   ├── vision_router.py      # Vision AI config & detection history
│   │   │   ├── voice_router.py       # Voice prompts & conversation logs
│   │   │   └── display_router.py     # Video streaming control for ESP32
│   │   └── websockets/               # Real-time WebSocket Gateway
│   │       ├── ws_manager.py         # Client & device connection manager
│   │       ├── ws_vision.py          # OV3660 camera stream & bounding box feedback
│   │       ├── ws_audio.py           # Full-duplex voice stream (Mic In -> TTS Out)
│   │       ├── ws_display.py         # Frame buffer stream to ESP32 screen
│   │       └── ws_telemetry.py       # Heartbeat & telemetry metrics stream
│   │
│   ├── core/                         # Core Configurations & Shared Infrastructure
│   │   ├── config.py                 # Pydantic-settings (.env management)
│   │   ├── database.py               # SQLAlchemy 2.0 Async Engine & SessionFactory
│   │   ├── redis.py                  # Async Redis Client & Pub/Sub Hub
│   │   ├── security.py               # Password hashing & JWT token validation
│   │   ├── exceptions.py             # Custom Application Exceptions & Handlers
│   │   └── logging.py                # Structured JSON logging setup
│   │
│   ├── modules/                      # DOMAIN MODULES BY HARDWARE/FEATURE
│   │   ├── auth/                     # Authentication Module
│   │   │   ├── models.py
│   │   │   ├── schemas.py
│   │   │   ├── repository.py
│   │   │   └── service.py
│   │   │
│   │   ├── devices/                  # Device Management & OTA Module
│   │   │   ├── models.py             # Device, TelemetryLog, FirmwareRelease
│   │   │   ├── schemas.py            # DeviceCreate, DeviceUpdate, TelemetryIn
│   │   │   ├── repository.py
│   │   │   ├── service.py            # Device provisioning & heartbeat tracking
│   │   │   └── ota_service.py        # Binary firmware handling & checksums
│   │   │
│   │   ├── vision/                   # Vision AI Module (OV3660 Camera)
│   │   │   ├── models.py             # DetectionHistory, AIModelConfig
│   │   │   ├── schemas.py            # FramePayload, BoundingBoxResult
│   │   │   ├── detector.py           # YOLO / Face Detector Engine (ONNX/Torch)
│   │   │   ├── frame_sampler.py      # Async Frame Drop / Buffer Strategy
│   │   │   └── service.py            # Frame ingestion -> detection -> action trigger
│   │   │
│   │   ├── voice/                    # Voice AI & Dialog Module (I2S Voice)
│   │   │   ├── models.py             # ConversationLog, VoiceIntent
│   │   │   ├── schemas.py            # AudioStreamChunk, AgentResponse
│   │   │   ├── vad.py                # Silero Voice Activity Detection
│   │   │   ├── stt_engine.py         # Faster-Whisper / Speech-To-Text engine
│   │   │   ├── llm_agent.py          # Agent Router & Tool Calling
│   │   │   ├── tts_engine.py         # Piper / Edge-TTS synthesis
│   │   │   └── service.py            # Voice dialog session coordinator
│   │   │
│   │   └── display/                  # Media & Screen Processing Module (TFT/OLED)
│   │       ├── models.py             # DisplaySession, MediaQueue
│   │       ├── schemas.py            # StreamRequest, TranscodeConfig
│   │       ├── yt_extractor.py       # YouTube link extractor (`yt-dlp`)
│   │       ├── ffmpeg_transcoder.py  # Resize, FPS downsample, RGB565 converter
│   │       └── service.py            # Frame buffer stream dispatch to ESP32
│   │
│   ├── integrations/                 # External Integrations
│   │   ├── storage.py                # S3 / MinIO client (Snapshots, OTA binaries)
│   │   └── mqtt_client.py            # Async MQTT v5 bridge client
│   │
│   ├── tasks/                        # Background Task Workers
│   │   ├── worker.py                 # Task entrypoint
│   │   ├── ai_heavy_tasks.py         # Batch video processing
│   │   └── cleanup_tasks.py          # Periodic frame buffer & log cleanup
│   │
│   └── main.py                       # FastAPI Factory, Middlewares, & Lifespan
│
├── tests/                            # Pytest Suites (Unit & Integration)
├── Dockerfile                        # Multi-stage Python 3.12 image
├── pyproject.toml                    # Dependency management (Poetry / UV)
└── alembic.ini
```

---

## 3. FRONTEND DIRECTORY STRUCTURE (VUE 3 + TAILWIND CSS SPA)

The frontend uses a Feature-based layout aligned directly with backend domain services:

```text
frontend/
├── public/                           # Static assets & favicon
├── src/
│   ├── assets/                       # Custom images & global fonts
│   ├── components/                   # Shared UI Components
│   │   ├── ui/                       # Base UI (Button, Modal, Input, Badge, Table)
│   │   ├── charts/                   # Telemetry Charts
│   │   └── layout/                   # Sidebar, Navbar, AppShell
│   │
│   ├── composables/                  # Reusable Vue Composables
│   │   ├── useWebSocket.ts           # WebSocket connection & auto-reconnect
│   │   ├── useAudioPlayer.ts         # Play TTS response audio
│   │   └── useVideoCanvas.ts         # Render MJPEG stream & bounding box canvas
│   │
│   ├── modules/                      # FEATURE MODULES
│   │   ├── auth/                     # Authentication & User Profile
│   │   │   ├── api/authApi.ts
│   │   │   ├── views/LoginView.vue
│   │   │   └── stores/authStore.ts
│   │   │
│   │   ├── devices/                  # Device management, metrics, & OTA hub
│   │   │   ├── api/deviceApi.ts
│   │   │   ├── components/DeviceCard.vue
│   │   │   ├── components/OtaUploadModal.vue
│   │   │   ├── views/DeviceListView.vue
│   │   │   ├── views/DeviceDetailView.vue
│   │   │   └── stores/deviceStore.ts
│   │   │
│   │   ├── vision/                   # Camera OV3660 monitor & AI overlay
│   │   │   ├── api/visionApi.ts
│   │   │   ├── components/LiveStreamViewer.vue
│   │   │   ├── components/DetectionHistoryTable.vue
│   │   │   └── views/VisionDashboardView.vue
│   │   │
│   │   ├── voice/                    # Voice AI Assistant console
│   │   │   ├── api/voiceApi.ts
│   │   │   ├── components/VoiceWaveVisualizer.vue
│   │   │   ├── components/ChatTranscript.vue
│   │   │   └── views/VoiceAssistantView.vue
│   │   │
│   │   └── display/                  # YouTube video streamer & screen control
│   │       ├── api/displayApi.ts
│   │       ├── components/YoutubeStreamControl.vue
│   │       ├── components/DisplayFramePreview.vue
│   │       └── views/DisplayManagerView.vue
│   │
│   ├── router/                       # Vue Router 4 (Guards & Lazy-loading)
│   ├── stores/                       # Global Pinia Stores
│   ├── services/                     # HTTP Client (Axios + Auto Token Refresh)
│   ├── styles/                       # Tailwind directives & global theme
│   ├── types/                        # TypeScript Interfaces & DTO definitions
│   ├── App.vue
│   └── main.ts
│
├── index.html
├── tailwind.config.js
├── vite.config.ts
└── tsconfig.json
```

---

## 4. ESP32 FIRMWARE STRUCTURE (ESP-IDF / FREERTOS C++)

```text
firmware/
├── include/
│   ├── config.h                      # Pinouts, Wi-Fi credentials, Server endpoints
│   ├── camera_driver.h               # OV3660 camera driver (SCCB, DVP, DMA)
│   ├── audio_driver.h                # I2S INMP441 Mic & MAX98357A Amp drivers
│   ├── display_driver.h              # ST7789 SPI TFT display driver (LVGL)
│   └── ws_client.h                   # WebSocket client (Binary & Text framing)
├── src/
│   ├── tasks/
│   │   ├── task_camera.cpp           # Task reading OV3660 frame -> stream to WS
│   │   ├── task_audio_in.cpp         # Task reading I2S Mic -> stream PCM to WS
│   │   ├── task_audio_out.cpp        # Task receiving PCM from WS -> write I2S DAC
│   │   ├── task_display.cpp          # Task receiving video frame -> render TFT screen
│   │   └── task_telemetry.cpp        # Task sending RAM/Wi-Fi metrics periodically
│   └── main.cpp                      # FreeRTOS initialization & Wi-Fi manager
└── platformio.ini                    # PlatformIO project configuration
```
