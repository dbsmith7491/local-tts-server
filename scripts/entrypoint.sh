#!/bin/bash
set -e

# Accept TTS license automatically by piping 'y' to Python
echo "y" | python -c "
from TTS.api import TTS
import sys
sys.stdin = open('/dev/tty', 'r') if sys.stdin.isatty() else sys.stdin
try:
    # This will trigger the license download and acceptance
    TTS('${TTS_MODEL:-tts_models/multilingual/multi-dataset/xtts_v2}')
except EOFError:
    pass
except Exception as e:
    print(f'Pre-initialization: {e}')
" 2>&1 | grep -v "EOF when reading" || true

# Now start the actual server
exec python -m uvicorn app.main:app --host "${SERVER_HOST:-0.0.0.0}" --port "${SERVER_PORT:-8000}" --ssl-keyfile "${SSL_KEY_PATH:-/app/certs/key.pem}" --ssl-certfile "${SSL_CERT_PATH:-/app/certs/cert.pem}"
