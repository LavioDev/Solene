# SYSTEM SPECIFICATION
## PROJECT: SOLENE IOT SMART HUB & AI PLATFORM

---

## 1. EXECUTIVE SUMMARY

Solene is an end-to-end Smart IoT & AI Platform. The system connects ESP32 microcontroller edge hardware with a high-performance backend built with Python 3.12 and FastAPI, alongside a real-time interactive administration dashboard powered by Vue 3 and Tailwind CSS (SPA).

Solene is identified as an AI companion robot (female persona identity) equipped with multi-modal capabilities:
1. IoT Vision & Deep Learning: Ingests real-time image/video streams from an OV3660 camera module on the ESP32, processes frames through Computer Vision models (Object Detection, Face Recognition, Gesture, Pose Estimation), and streams back visual overlay results or triggers hardware actions.
2. Interactive Audio & Voice AI: Captures speech via an I2S microphone, converts speech to text (STT), understands context and intent through a Large Language Model (LLM Agent), executes automated function calling, and synthesizes natural speech (TTS) sent back to the I2S speaker on the ESP32.
3. Display & Media Streaming: Processes media content (such as YouTube videos, live camera feeds, and custom UI facial expressions), transcodes/downsamples color spaces (RGB565/JPEG) optimized for ESP32 display constraints (TFT/OLED/SPI LCD), and streams frames to the device.
4. IoT Device Management & Core CRUD: Manages the complete device lifecycle (Device Registry, Pairing, Provisioning, Telemetry Ingestion, Remote Configuration, Over-The-Air Firmware Updates, and Role-Based Access Control).

---

## 2. EDGE HARDWARE SPECIFICATION (ESP32)

```
+-------------------------------------------------------------------------+
|                              ESP32 HARDWARE                             |
|                                                                         |
|  +--------------------+   +--------------------+   +-----------------+  |
|  | Camera Module      |   | Audio Codec (I2S)  |   | Display Module  |  |
|  | - OV3660 (QSXGA)   |   | - INMP441 / ICS43434|  | - ST7789/ILI9341|  |
|  | - DVP/MIPI interfac|   | - MAX98357A / ES8388|  | - SPI/8-bit Para|  |
|  +---------+----------+   +---------+----------+   +--------+--------+  |
|            |                        |                       |           |
|            +-------------------+    |    +------------------+           |
|                                |    |    |                              |
|                       +--------v----v----v--------+                     |
|                       |    ESP32-S3 (Dual-Core)   |                     |
|                       |   8MB PSRAM + 16MB Flash  |                     |
|                       |      FreeRTOS + Wi-Fi     |                     |
|                       +-------------+-------------+                     |
+-------------------------------------|-----------------------------------+
                                      | (Protocols: MQTT / WebSockets / HTTP2)
                                      v
```

### Hardware Component Specifications:
- MCU: ESP32-S3 (or standard ESP32 with minimum 4MB - 8MB PSRAM for frame buffering).
- Vision (OV3660): Supports resolutions up to 3MP (2048x1536), outputting compressed JPEG or RGB565/YUV bytes.
- Audio Input: I2S Digital Microphone (e.g., INMP441 or ES8388 Audio DAC/ADC).
- Audio Output: I2S DAC/Amplifier (e.g., MAX98357A).
- Display: SPI TFT Color Display (ST7789 / ILI9341 / GC9A01) with standard resolutions of 240x240, 320x240, or 480x320.

---

## 3. FUNCTIONAL REQUIREMENTS

### 3.1. Vision & Deep Learning Module

| Requirement ID | Function Name | Detailed Description |
| :--- | :--- | :--- |
| FR-VIS-01 | Camera Ingestion | Ingest JPEG frames or MJPEG streams from ESP32 via WebSocket or HTTP Chunked POST. |
| FR-VIS-02 | Frame Queue & Sampling | Buffer incoming frames into an async queue, automatically dropping stale frames under heavy load to guarantee zero-lag real-time processing. |
| FR-VIS-03 | Deep Learning Pipeline | Execute Computer Vision models (YOLOv8/v11, Face Recognition, PoseNet) via ONNX Runtime / PyTorch / TensorRT. |
| FR-VIS-04 | Visual Telemetry & Overlay | Attach bounding boxes, labels, and confidence scores onto frames and broadcast them to Vue 3 Dashboard via WebSocket. |
| FR-VIS-05 | Action Triggering | Execute automated control logic upon specific object detection events (e.g., unlock door when a authorized face is verified). |

---

### 3.2. Audio, Voice AI & Agent Module

| Requirement ID | Function Name | Detailed Description |
| :--- | :--- | :--- |
| FR-AUD-01 | Audio Ingestion & VAD | Receive raw PCM audio stream (16kHz, 16-bit Mono) from ESP32 over WebSocket. Use Silero Voice Activity Detection (VAD) to segment speech starts and ends. |
| FR-AUD-02 | Speech-to-Text (STT) | Convert recorded speech chunks to text with low latency (Faster-Whisper / Whisper.cpp / Deepgram). |
| FR-AUD-03 | LLM Agent & Function Calling | Parse intent and context, generate responses, and trigger tool function calls (e.g., `turn_on_light()`, `display_video()`, `get_sensor_data()`). |
| FR-AUD-04 | Text-to-Speech (TTS) | Synthesize speech audio (PCM/MP3/Opus) from response text (Edge-TTS, Piper, Kokoro TTS). |
| FR-AUD-05 | Audio Downlink Stream | Stream synthesized audio back to ESP32 over WebSocket in small chunks for immediate playback on the I2S speaker. |

---

### 3.3. Media & Display Streaming Module

| Requirement ID | Function Name | Detailed Description |
| :--- | :--- | :--- |
| FR-DSP-01 | Video Source Fetcher | Fetch video streams from YouTube (`yt-dlp`), RTSP cameras, or local media files on request. |
| FR-DSP-02 | Transcoding & Scaling Engine | Use FFmpeg / OpenCV to resize resolution matching ESP32 screen dimensions (e.g., 320x240), downsample frame rate (10-20 FPS), and optimize color space (RGB565). |
| FR-DSP-03 | Frame Buffer Optimization | Compress frames into small JPEG chunks or raw RLE/ZSTD compressed byte arrays to optimize Wi-Fi bandwidth and hardware decoding. |
| FR-DSP-04 | Display Control Protocol | Transmit display commands: UI layout switching (LVGL), notification text overlay, static images, or live video streaming. |

---

### 3.4. IoT Core & Device Management Module

| Requirement ID | Function Name | Detailed Description |
| :--- | :--- | :--- |
| FR-IOT-01 | Device Registration & Pairing | Manage device inventories (Device ID, MAC Address, Chip ID, Firmware Version, Secret Keys). |
| FR-IOT-02 | Device State & Heartbeat | Track Online/Offline states, Wi-Fi RSSI signal strength, battery voltage, and free heap/PSRAM. |
| FR-IOT-03 | Telemetry Data Ingestion | Store and plot time-series metrics (temperature, ambient light, CPU load). |
| FR-IOT-04 | OTA Firmware Management | Manage binary firmware releases and distribute Over-The-Air updates securely verified with SHA-256 checksums. |
| FR-IOT-05 | Remote Configuration | Dynamically update ESP32 operating parameters (Camera frame rate, Audio Gain, Screen Brightness, AI Thresholds). |
| FR-IOT-06 | RBAC & Multi-tenancy | User access management, device grouping, permissions, and audit logging. |

---

### 3.5. Web Administration SPA (Vue 3 + Tailwind CSS)

| Requirement ID | Function Name | Detailed Description |
| :--- | :--- | :--- |
| FR-UI-01 | Realtime Device Dashboard | Monitor status and metrics for all connected ESP32 devices in real time. |
| FR-UI-02 | Live Vision Monitor | View live OV3660 camera stream, toggle AI bounding box overlays, and capture snapshots. |
| FR-UI-03 | Voice Assistant Console | Chat interface interacting with Solene, view voice transcripts, and inspect executed function calls. |
| FR-UI-04 | Display Stream Manager | Input YouTube links or media files, preview live transcoding, and push stream to ESP32 display. |
| FR-UI-05 | Device Settings & OTA Hub | Configure device parameters, upload `.bin` firmware files, and trigger batch updates. |

---

## 4. NON-FUNCTIONAL REQUIREMENTS

1. Low Latency:
   - Vision AI inference: < 150ms / frame.
   - Voice interaction roundtrip (Audio In -> STT -> LLM -> TTS -> Audio Out): < 1.5s - 2.5s.
   - Video stream delay to ESP32: < 300ms.
2. Scalability:
   - Backend cleanly decouples API I/O handling from AI Inference and Heavy Media Workers to scale GPU/CPU workers independently.
3. Resilience & Fault Tolerance:
   - Automatic reconnection handling, heartbeat monitoring, and message queuing for intermittent Wi-Fi connectivity.
4. Security:
   - Device authentication via HMAC-SHA256 tokens or mTLS (Mutual TLS).
   - Per-device rate limiting to protect against unauthorized spam or Denial-of-Service attacks.
