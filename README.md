# Jim TTS Server

Drunk dart commentator TTS service with voice cloning and personality enhancement.

## Quick Start

### Prerequisites
- Docker & Docker Compose
- (Optional) NVIDIA GPU with CUDA support

### Setup

1. Clone repository
2. Generate SSL certificates:
   ```bash
   chmod +x scripts/generate_cert.sh
   ./scripts/generate_cert.sh
   ```

3. Add voice sample:
   ```bash
   # Copy your jim_voice.wav to voices/
   cp /path/to/jim_voice.wav voices/
   ```

4. Start server (CPU):
   ```bash
   docker-compose up --build
   ```

   Or with GPU:
   ```bash
   docker-compose -f docker-compose.yml -f docker-compose.gpu.yml up --build
   ```

5. Test server:
   ```bash
   python scripts/test_server.py
   ```

### API Usage

**Generate commentary:**
```bash
curl -X POST "https://localhost:8000/tts/generate?text=Nice%20throw!&quality=great" \
  --output jim_comment.wav -k
```

**Batch pre-generate:**
```bash
curl -X POST "https://localhost:8000/tts/batch-pregenerate" \
  -H "Content-Type: application/json" \
  -d '[{"text":"Great!","quality":"great"},{"text":"Miss!","quality":"miss"}]' -k
```

### iOS Setup

1. Visit `https://YOUR_SERVER_IP:8000/download-cert` in Safari
2. Install certificate profile
3. Trust in Settings → General → About → Certificate Trust Settings

## Development

### Project Structure
- `app/` - Main application code
- `scripts/` - Utility scripts
- `voices/` - Voice samples for cloning
- `cache/` - Audio cache
- `certs/` - SSL certificates

### Environment Variables
See `.env.example` for all configuration options.

## Deployment

### Transfer to Another Machine
```bash
# Save container
docker save jim-tts-server:latest > jim-tts.tar

# On new machine
docker load < jim-tts.tar
docker-compose up
```

### AWS Deployment (Future)
See deployment docs for ECS/Fargate setup.
