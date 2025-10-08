# Local TTS Server

High-quality voice cloning TTS server with personality transformations and multi-platform support.

## Features

- 🎙️ **Voice Cloning**: Clone any voice from a 6-10 second audio sample
- ⚡ **GPU Acceleration**: CUDA support for fast generation on NVIDIA GPUs
- 🍎 **Apple Silicon**: MLX-Audio support for M1/M2/M3 Macs
- 🎭 **Personality Transforms**: Apply text transformations for character voices
- 💾 **Smart Caching**: In-memory and disk caching for instant responses
- 🔒 **HTTPS**: Built-in SSL for secure communication
- 🐳 **Docker**: Easy deployment with Docker Compose

## Quick Start

### Prerequisites
- **Docker & Docker Compose**
- **(Optional)** NVIDIA GPU with CUDA support for fast generation
- **(Optional)** Apple Silicon Mac for MLX-Audio acceleration

### Basic Setup

1. **Clone repository**
   ```bash
   git clone https://github.com/dbsmith7491/local-tts-server.git
   cd local-tts-server
   ```

2. **Generate SSL certificates**
   ```bash
   chmod +x scripts/generate_cert.sh
   ./scripts/generate_cert.sh
   ```

3. **Add your voice sample**
   ```bash
   # Copy a 6-10 second voice sample (WAV, 22050 Hz recommended)
   cp /path/to/your_voice.wav voices/speaker.wav
   ```

4. **Start the server**

   **CPU (slower):**
   ```bash
   docker-compose up -d
   ```

   **GPU (NVIDIA - recommended):**
   ```bash
   docker-compose -f docker-compose.gpu.yml up -d
   ```

5. **Test the server**
   ```bash
   # Health check
   curl -k https://localhost:8000/health

   # Generate audio
   curl -k -X POST "https://localhost:8000/tts/generate?text=Hello%20world" \
     --output test.wav
   ```

## API Endpoints

### Generate Audio
```bash
POST /tts/generate?text=YOUR_TEXT&use_personality=true
```

**Parameters:**
- `text` (required): Text to synthesize
- `quality` (optional): Mood/quality hint (`great`, `good`, `okay`, `bad`, `miss`)
- `use_personality` (optional): Apply personality transformations (default: `true`)

**Response:** WAV audio file

**Example:**
```bash
curl -k -X POST "https://localhost:8000/tts/generate?text=Nice%20work" \
  --output audio.wav
```

### Health Check
```bash
GET /health
```
Returns server status and configuration info.

### Cache Management
```bash
GET /cache/stats      # View cache statistics
POST /cache/clear     # Clear audio cache
```

### Download Certificate (for mobile devices)
```bash
GET /download-cert
```
Download SSL certificate for iOS/Android installation.

## Configuration

Create a `.env` file (copy from `.env.example`):

```bash
# Voice Settings
SPEAKER_WAV=/app/voices/speaker.wav

# Server Settings
SERVER_HOST=0.0.0.0
SERVER_PORT=8000
LOG_LEVEL=INFO

# TTS Settings
TTS_MODEL=tts_models/multilingual/multi-dataset/xtts_v2
TTS_DEVICE=cuda  # or 'cpu'
PREGENERATE_ON_STARTUP=true

# SSL Settings
SSL_CERT_PATH=/app/certs/cert.pem
SSL_KEY_PATH=/app/certs/key.pem

# CORS
CORS_ORIGINS=["*"]
```

## Platform Support

| Platform | Engine | Performance |
|----------|--------|------------|
| **NVIDIA GPU** | XTTS + CUDA | ⚡ 1-2 sec/phrase |
| **Apple Silicon** | MLX-Audio | 🚀 Fast (experimental) |
| **CPU** | XTTS | 🐌 Slow (~4 min/phrase) |

The server automatically detects your platform and selects the best TTS engine.

## iOS/Mobile Setup

1. Visit `https://YOUR_SERVER_IP:8000/download-cert` in Safari
2. Install the certificate profile
3. Go to **Settings → General → About → Certificate Trust Settings**
4. Enable trust for the certificate

## Development

### Project Structure
```
local-tts-server/
├── app/
│   ├── main.py              # FastAPI application
│   ├── tts_engine.py        # TTS engine factory
│   ├── tts_engine_xtts.py   # XTTS implementation (GPU/CPU)
│   ├── tts_engine_mlx.py    # MLX-Audio (Apple Silicon)
│   ├── jim_personality.py   # Text transformation engine
│   ├── cache_manager.py     # Audio caching system
│   └── config.py            # Configuration management
├── voices/                   # Voice samples (not in git)
├── cache/                    # Cached audio files
├── certs/                    # SSL certificates (generate locally)
├── scripts/                  # Utility scripts
└── requirements.txt          # Python dependencies
```

### Running Locally (without Docker)

**macOS:**
```bash
pip install -r requirements-macos.txt
cp .env.example .env
# Edit .env for local paths
python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8000
```

**Linux/Windows:**
```bash
pip install -r requirements.txt
cp .env.example .env
# Edit .env for local paths
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
```

## Deployment

### Docker Image Transfer
```bash
# Save container
docker save local-tts-server:latest > tts-server.tar

# Load on another machine
docker load < tts-server.tar
docker-compose up -d
```

### Cloud Deployment
See [SETUP.md](SETUP.md) for detailed AWS/cloud deployment instructions.

## Performance Tips

1. **Use GPU**: NVIDIA GPU provides 100x+ speedup over CPU
2. **Enable Caching**: Set `PREGENERATE_ON_STARTUP=true` for common phrases
3. **Adjust Quality**: Lower quality settings generate faster
4. **Voice Sample**: Use clean, 22050 Hz mono audio for best results

## Troubleshooting

**GPU not detected?**
```bash
nvidia-smi  # Check NVIDIA driver
docker run --rm --gpus all nvidia/cuda:12.1.0-base-ubuntu22.04 nvidia-smi
```

**Slow generation?**
- Check `docker logs local-tts-server` for errors
- Verify GPU is being used (check health endpoint)
- Try disabling pre-generation

**Certificate issues?**
```bash
./scripts/generate_cert.sh  # Regenerate certificates
```

## License

See LICENSE file for details.

## Credits

Built with:
- [Coqui TTS](https://github.com/coqui-ai/TTS) - XTTS v2 voice cloning
- [MLX-Audio](https://github.com/Blaizzy/mlx-audio) - Apple Silicon acceleration
- [FastAPI](https://fastapi.tiangolo.com/) - Web framework

🤖 Created with [Claude Code](https://claude.com/claude-code)
