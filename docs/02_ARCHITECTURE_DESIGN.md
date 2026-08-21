# SYSTEM ARCHITECTURE DESIGN
## PROJECT: SOLENE IOT SMART HUB & AI PLATFORM

---

## 1. END-TO-END TOPOLOGY OVERVIEW

```mermaid
flowchart TB
    subgraph ESP32_Edge["ESP32 Edge Device Layer"]
        OV["OV3660 Camera"]
        MIC["I2S Microphone"]
        SPK["I2S Speaker"]
        DISP["SPI TFT Display"]
        CORE_ESP["ESP32-S3 Firmware (FreeRTOS Tasks)"]
        
        OV --> CORE_ESP
        MIC --> CORE_ESP
        CORE_ESP --> SPK
        CORE_ESP --> DISP
    end

    subgraph Ingress["Ingress / Gateway Layer"]
        Traefik["Traefik / Nginx (TLS Termination & Reverse Proxy)"]
        EMQX["MQTT Broker (EMQX / Mosquitto)"]
    end

    subgraph Backend_App["FastAPI Backend Cluster (Python 3.12)"]
        WS_Gateway["WebSocket Hub (IoT & Client Conns)"]
        REST_API["FastAPI REST Endpoints (CRUD & Auth)"]
        
        subgraph DeviceModules["Device Domain Services"]
            VisionService["Vision Domain Service"]
            AudioService["Audio & Voice AI Service"]
            DisplayService["Display Stream Service"]
            DeviceService["Device Registry & OTA Service"]
        end
    end

    subgraph AI_Media_Workers["AI & Media Worker Engine"]
        YOLO_Worker["Vision AI Inference (YOLO/ONNX/TensorRT)"]
        Voice_Worker["Speech AI Pipeline (Whisper + LLM + TTS)"]
        Media_Worker["FFmpeg Video Transcoding (YouTube / Media)"]
    end

    subgraph Storage_Layer["Data & Persistence Layer"]
        Postgres[(PostgreSQL + TimescaleDB)]
        RedisCache[(Redis - Cache, Pub/Sub, Queue)]
        MinIO[(MinIO / S3 - Media, Snapshots, Firmware)]
    end

    subgraph Client_App["Frontend SPA Layer"]
        VueSPA["Vue 3 SPA (Vite + Tailwind + Pinia + VueQuery)"]
    end

    %% ESP32 Connections
    CORE_ESP <== "WS: Video/Audio Stream & Display frames" ==> WS_Gateway
    CORE_ESP <== "MQTT: Telemetry & Commands" ==> EMQX

    %% Ingress to App
    EMQX <== "Internal Bridge" ==> WS_Gateway
    Traefik --> REST_API
    Traefik --> WS_Gateway

    %% App to Domain Services
    REST_API --> DeviceService & VisionService & AudioService & DisplayService
    WS_Gateway --> DeviceService & VisionService & AudioService & DisplayService

    %% Services to Async Workers
    VisionService <== "Redis Stream / ZeroMQ" ==> YOLO_Worker
    AudioService <== "Async Pipeline / Celery" ==> Voice_Worker
    DisplayService <== "FFmpeg Subprocess / Worker" ==> Media_Worker

    %% Persistence
    DeviceService --> Postgres
    VisionService --> MinIO
    DisplayService --> MinIO
    WS_Gateway <--> RedisCache

    %% Frontend Connection
    VueSPA <== "HTTPS / WSS" ==> Traefik
```

---

## 2. COMMUNICATION PROTOCOLS MATRIX

To balance RAM constraints on the ESP32 and low latency requirements for AI, the system uses a hybrid protocol design:

| Communication Channel | Protocol | Payload Format | Usage Purpose |
| :--- | :--- | :--- | :--- |
| Telemetry & Heartbeat | MQTT v5 / TLS | Compact JSON / MsgPack | Transmit temperature, RAM, Wi-Fi RSSI, and receive GPIO trigger commands. |
| Camera Ingestion | WebSocket Binary / HTTP Chunked | JPEG Byte Array + Packet Header | Stream camera frames from OV3660 to backend for AI inference. |
| Voice Input / Output | WebSocket Full-Duplex | Raw PCM 16kHz 16-bit Mono (20ms-50ms Chunks) | Record user speech audio and stream back AI synthesized speech response. |
| Display Streaming | WebSocket Binary / TCP Stream | MJPEG / RGB565 Chunks (Header + Pixel Array) | Stream transcoded video frames down to the ESP32 display. |
| Firmware OTA | HTTPS (Range requests) | Binary file (`.bin`) | Download firmware binary with SHA-256 validation. |
| Web Client SPA | REST API + WebSockets | JSON + WebRTC / WSS | System administration, configuration, and live stream viewing. |

---

## 3. AI & MEDIA PIPELINE DESIGNS

### 3.1. Vision & Deep Learning Pipeline

```mermaid
sequenceDiagram
    autonumber
    participant ESP as ESP32 (OV3660)
    participant WS as FastAPI WebSocket Hub
    participant Sampler as Frame Buffer & Drop Sampler
    participant AI as Vision Inference Engine (YOLO/ONNX)
    participant Cache as Redis Pub/Sub
    participant Web as Vue 3 SPA Client

    ESP->>WS: Send Binary Frame (JPEG)
    WS->>Sampler: Enqueue Frame Buffer
    Note over Sampler: Drop old frames if worker is busy (Zero-Lag)
    Sampler->>AI: Batch / Single Frame Tensor
    AI->>AI: Model Inference (Detect, Classify, Track)
    AI->>Cache: Publish Bounding Boxes & Detection Event
    Cache->>Web: WebSocket Broadcast (Overlay Bounding Box)
    alt Action Triggered
        AI->>ESP: Send response command (e.g., toggle GPIO / unlock)
    end
```

### 3.2. Conversational Audio & Voice AI Pipeline

```mermaid
sequenceDiagram
    autonumber
    participant ESP as ESP32 (Mic/Speaker)
    participant WS as Audio WebSocket Service
    participant VAD as Silero VAD (Voice Activity)
    participant STT as Faster-Whisper (Speech-To-Text)
    participant LLM as LLM Agent & Function Router
    participant TTS as TTS Engine (Piper/Edge-TTS)

    loop Continuous Audio Input
        ESP->>WS: Stream PCM Audio Chunks (16kHz, 16-bit)
        WS->>VAD: Analyze voice presence
    end
    Note over VAD: Detect speech end (Silence Threshold ~ 500ms)
    VAD->>STT: Send buffered audio
    STT-->>LLM: Transcribed Text ("Play animation on the screen")
    LLM->>LLM: Parse intent & trigger Function Calling
    par Execute Function
        LLM->>WS: Trigger `display_youtube_video(query="animation")`
    and Synthesize Voice Response
        LLM->>TTS: "Starting animation display for you now."
        TTS->>WS: Stream Audio Chunks (PCM/Opus)
        WS->>ESP: Stream audio chunks to ESP32 speaker
    end
```

### 3.3. YouTube Transcoding & Display Pipeline

```mermaid
flowchart LR
    UserRequest["Request: YouTube Link"] --> Fetcher["yt-dlp Stream Extractor"]
    Fetcher --> FFmpeg["FFmpeg Transcoder Engine"]
    
    subgraph TranscodeConfig["ESP32 Optimization"]
        FFmpeg --> Scale["Resize: 320x240 / 240x240"]
        Scale --> FPS["Downsample: 15-20 FPS"]
        FPS --> Format["Format: MJPEG or RGB565 Stream"]
    end
    
    Format --> StreamQueue["Async Frame Queue"]
    StreamQueue --> WS_Display["FastAPI Display Service"]
    WS_Display ==> "Binary WebSocket" ==> ESP_Disp["ESP32 DMA Frame Buffer -> TFT Screen"]
```

---

## 4. DATABASE ERD SCHEMA

The platform uses PostgreSQL 16 with TimescaleDB support for telemetry:

```mermaid
erDiagram
    USERS ||--o{ DEVICES : owns
    DEVICES ||--o{ TELEMETRY_LOGS : records
    DEVICES ||--o{ DEVICE_EVENTS : generates
    DEVICES ||--o{ AI_DETECTIONS : captures
    DEVICES }o--|| FIRMWARE_RELEASES : runs

    USERS {
        uuid id PK
        string email UK
        string hashed_password
        string role
        boolean is_active
        timestamp created_at
    }

    DEVICES {
        uuid id PK
        uuid user_id FK
        string device_code UK
        string name
        string mac_address UK
        string chip_type
        jsonb hardware_capabilities
        jsonb current_config
        string status
        timestamp last_seen_at
        timestamp created_at
    }

    TELEMETRY_LOGS {
        int64 id PK
        uuid device_id FK
        float cpu_temperature
        int free_heap
        int wifi_rssi
        float battery_voltage
        jsonb custom_metrics
        timestamp recorded_at
    }

    AI_DETECTIONS {
        uuid id PK
        uuid device_id FK
        string module_type
        string detected_label
        float confidence
        jsonb bounding_box
        string snapshot_s3_url
        timestamp created_at
    }

    FIRMWARE_RELEASES {
        uuid id PK
        string version UK
        string target_chip
        string binary_s3_url
        string sha256_checksum
        jsonb changelog
        boolean is_stable
        timestamp released_at
    }
```
