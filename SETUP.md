# Local TTS Server - Setup Guide

## Quick Overview

This server provides voice cloning TTS with automatic platform detection:
- **macOS (M1/M2/M3)**: Uses MLX-Audio (currently buggy, falls back to CPU)
- **Windows/Linux + NVIDIA GPU**: Uses XTTS with CUDA ⚡ **FAST**
- **CPU fallback**: Works but slow (~4min/phrase)

---

## Setup on RTX 5090 Desktop (RECOMMENDED)

### Prerequisites

**For Windows:**
1. **Docker Desktop** with WSL2
   - Download: https://www.docker.com/products/docker-desktop
   - During install: Enable WSL2 backend
2. **NVIDIA Container Toolkit**
   ```powershell
   # In PowerShell as Administrator
   wsl --install
   # Restart, then install NVIDIA toolkit in WSL:
   wsl
   distribution=$(. /etc/os-release;echo $ID$VERSION_ID)
   curl -s -L https://nvidia.github.io/nvidia-docker/gpgkey | sudo apt-key add -
   curl -s -L https://nvidia.github.io/nvidia-docker/$distribution/nvidia-docker.list | sudo tee /etc/apt/sources.list.d/nvidia-docker.list
   sudo apt-get update && sudo apt-get install -y nvidia-container-toolkit
   sudo systemctl restart docker
   ```

**For Linux:**
1. **Docker Engine**
   ```bash
   curl -fsSL https://get.docker.com -o get-docker.sh
   sudo sh get-docker.sh
   sudo usermod -aG docker $USER
   # Log out and back in
   ```
2. **NVIDIA Container Toolkit**
   ```bash
   distribution=$(. /etc/os-release;echo $ID$VERSION_ID)
   curl -s -L https://nvidia.github.io/nvidia-docker/gpgkey | sudo apt-key add -
   curl -s -L https://nvidia.github.io/nvidia-docker/$distribution/nvidia-docker.list | sudo tee /etc/apt/sources.list.d/nvidia-docker.list
   sudo apt-get update && sudo apt-get install -y nvidia-container-toolkit
   sudo systemctl restart docker
   ```

### Installation Steps

1. **Clone the repository**
   ```bash
   git clone https://github.com/dbsmith7491/local-tts-server.git
   cd local-tts-server
   ```

2. **Copy your voice file**
   ```bash
   # Copy jim_voice.wav to voices/ directory
   # Or use any other voice sample (6-10 seconds of clear speech)
   cp /path/to/your/voice.wav voices/jim_voice.wav
   ```

3. **Generate SSL certificates**
   ```bash
   # On Linux/WSL:
   ./scripts/generate_cert.sh

   # On Windows (Git Bash):
   bash scripts/generate_cert.sh
   ```

4. **Configure environment (optional)**
   ```bash
   # Copy example env file
   cp .env.example .env

   # Edit .env to customize:
   # - SPEAKER_WAV path
   # - SERVER_PORT
   # - PREGENERATE_ON_STARTUP (true/false)
   ```

5. **Start the server with GPU**
   ```bash
   docker-compose -f docker-compose.gpu.yml up -d
   ```

6. **Check logs**
   ```bash
   docker-compose logs -f
   ```

   Look for:
   ```
   ✅ TTS model loaded: tts_models/multilingual/multi-dataset/xtts_v2
   ✅ Using voice clone: /app/voices/jim_voice.wav
   ✅ Server ready! TTS engine loaded and standing by...
   ```

7. **Test the server**
   ```bash
   # Health check
   curl -k https://localhost:8000/health

   # Generate audio
   curl -k -X POST "https://localhost:8000/tts/generate?text=Hello%20world" \
     --output test.wav
   ```

---

## Expected Performance

| Platform | Engine | Speed per Phrase |
|----------|--------|-----------------|
| **RTX 5090** | XTTS + CUDA | 🚀 **1-2 seconds** |
| MacBook M1 | XTTS + CPU | 🐌 ~4 minutes |
| MacBook M1 | MLX-Audio | ⚠️ Currently buggy |

---

## API Endpoints

**Base URL**: `https://localhost:8000`

### `GET /health`
Check server status

### `POST /tts/generate`
Generate TTS audio

**Parameters:**
- `text` (required): Text to synthesize
- `quality` (optional): `great`, `good`, `okay`, `bad`, `miss`
- `use_personality` (optional): Enable drunk personality (default: true)

**Example:**
```bash
curl -k -X POST "https://localhost:8000/tts/generate?text=Nice%20throw" \
  --output audio.wav
```

### `GET /cache/stats`
View cache statistics

### `POST /cache/clear`
Clear audio cache

### `GET /download-cert`
Download SSL certificate for mobile devices

---

## Troubleshooting

### GPU Not Detected
```bash
# Check NVIDIA driver
nvidia-smi

# Check Docker can see GPU
docker run --rm --gpus all nvidia/cuda:12.1.0-base-ubuntu22.04 nvidia-smi
```

### "CUDA out of memory"
Reduce batch size or lower TTS model size in config

### SSL Certificate Issues
Regenerate certificates:
```bash
./scripts/generate_cert.sh
```

### Slow Generation on GPU
Check Docker logs for errors:
```bash
docker logs local-tts-server
```

### Pre-generation Taking Too Long
Set `PREGENERATE_ON_STARTUP=false` in docker-compose.yml

---

## File Structure

```
local-tts-server/
├── app/
│   ├── main.py              # FastAPI app
│   ├── tts_engine.py        # TTS engine factory
│   ├── tts_engine_xtts.py   # XTTS implementation
│   ├── tts_engine_mlx.py    # MLX-Audio (macOS)
│   ├── jim_personality.py   # Text transformations
│   ├── cache_manager.py     # Audio caching
│   └── config.py            # Settings
├── voices/
│   └── jim_voice.wav        # Your voice sample (not in git)
├── certs/
│   ├── cert.pem             # SSL cert (generate with script)
│   └── key.pem              # SSL key (generate with script)
├── cache/                   # Cached audio files
├── docker-compose.yml       # CPU deployment
├── docker-compose.gpu.yml   # GPU deployment ⚡
└── requirements.txt         # Python dependencies
```

---

## Updating

```bash
cd local-tts-server
git pull
docker-compose -f docker-compose.gpu.yml down
docker-compose -f docker-compose.gpu.yml build
docker-compose -f docker-compose.gpu.yml up -d
```

---

## Stopping the Server

```bash
docker-compose -f docker-compose.gpu.yml down
```

---

## macOS Development (Native - No Docker)

If running natively on macOS for development:

```bash
# Install dependencies
pip install -r requirements-macos.txt

# Create .env file
cp .env.example .env

# Edit .env for local paths:
SPEAKER_WAV=./voices/jim_voice.wav
CACHE_DIR=./cache/pregenerated
SSL_CERT_PATH=./certs/cert.pem
SSL_KEY_PATH=./certs/key.pem

# Run server
python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8000
```

**Note**: MLX-Audio has a current bug. Server will fall back to XTTS CPU (slow).

---

## Next Steps

1. ✅ Get it running on RTX 5090 (super fast)
2. 🔧 Fix MLX-Audio bug for fast macOS development (optional)
3. ☁️ Deploy to AWS/cloud for 24/7 availability (optional)

---

## Support

Created with Claude Code: https://claude.com/claude-code

Repository: https://github.com/dbsmith7491/local-tts-server
