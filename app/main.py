from fastapi import FastAPI, HTTPException
from fastapi.responses import Response, FileResponse
from fastapi.middleware.cors import CORSMiddleware
import socket
import logging
from pathlib import Path
from typing import Optional

from .tts_engine import create_tts_engine
from .tts_base import BaseTTSEngine
from .jim_personality import JimPersonality
from .cache_manager import AudioCacheManager
from .config import settings

# Setup logging
logging.basicConfig(
    level=getattr(logging, settings.log_level),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Local TTS Server",
    version="1.0.0",
    description="Voice cloning TTS service with personality transformations"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global instances
tts_engine: Optional[BaseTTSEngine] = None
jim_personality: Optional[JimPersonality] = None
cache_manager: Optional[AudioCacheManager] = None

def get_local_ip():
    """Get local IP address"""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
        s.close()
        return local_ip
    except Exception:
        return "Unable to determine"

@app.on_event("startup")
async def startup_event():
    """Initialize TTS engine"""
    global tts_engine, jim_personality, cache_manager

    local_ip = get_local_ip()

    logger.info("=" * 70)
    logger.info("🎙️  Local TTS Server Starting...")
    logger.info("=" * 70)
    logger.info(f"📡 Network: https://{local_ip}:{settings.server_port}")
    logger.info("=" * 70)

    try:
        logger.info("Loading TTS model...")
        logger.info(f"Platform detected: {settings.selected_engine}")
        tts_engine = create_tts_engine(
            model_name=settings.tts_model,
            device=settings.tts_device,
            speaker_wav=settings.speaker_wav
        )

        jim_personality = JimPersonality()
        cache_manager = AudioCacheManager(
            tts_engine,
            jim_personality,
            cache_dir=settings.cache_dir
        )

        if settings.pregenerate_on_startup:
            logger.info("Pre-generating common phrases...")
            await cache_manager.pregenerate_common_phrases()

        logger.info("=" * 70)
        logger.info("✅ Server ready! TTS engine loaded and standing by...")
        logger.info("=" * 70)

    except Exception as e:
        logger.error(f"Failed to initialize: {e}")
        raise

@app.get("/")
async def root():
    """Server info"""
    return {
        "status": "online",
        "message": "Local TTS Server - Voice Cloning Edition",
        "version": "1.0.0",
        "protocol": "HTTPS",
        "endpoints": {
            "health": "/health",
            "generate": "/tts/generate",
            "batch": "/tts/batch-pregenerate",
            "certificate": "/download-cert",
            "cache_stats": "/cache/stats"
        }
    }

@app.get("/health")
async def health():
    """Health check"""
    return {
        "status": "healthy",
        "tts_engine": "loaded" if tts_engine else "not loaded",
        "gpu_available": tts_engine.is_gpu_available() if tts_engine else False,
        "cached_items": cache_manager.get_cache_size() if cache_manager else 0,
        "model": tts_engine.get_voice_info() if tts_engine else None
    }

@app.get("/download-cert")
async def download_certificate():
    """Download SSL certificate for iOS installation"""
    cert_path = Path(settings.ssl_cert_path)
    if not cert_path.exists():
        raise HTTPException(status_code=404, detail="Certificate not found")

    return FileResponse(
        cert_path,
        media_type="application/x-pem-file",
        filename="local-tts-server.pem"
    )

@app.post("/tts/generate")
async def generate_commentary(
    text: str,
    quality: Optional[str] = None,
    use_personality: bool = True
) -> Response:
    """
    Generate single commentary audio

    Args:
        text: Commentary text
        quality: Throw quality (great, good, okay, bad, miss, bust, game_winner)
        use_personality: Apply Jim's personality transformation

    Returns:
        WAV audio file
    """
    if not tts_engine:
        raise HTTPException(status_code=503, detail="TTS engine not ready")

    try:
        # Check cache first
        cached = cache_manager.get_cached(text)
        if cached:
            logger.info(f"Cache hit: {text[:50]}...")
            return Response(
                content=cached,
                media_type="audio/wav",
                headers={"X-Cache": "HIT"}
            )

        # Generate
        logger.info(f"Generating: {text[:50]}...")

        enhanced = jim_personality.enhance_text(text, quality) if use_personality else text
        audio = await tts_engine.generate_audio(enhanced)

        # Cache and return
        cache_manager.cache_audio(text, audio)

        return Response(
            content=audio,
            media_type="audio/wav",
            headers={"X-Cache": "MISS"}
        )

    except Exception as e:
        logger.error(f"Generation error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/tts/batch-pregenerate")
async def batch_pregenerate(items: list[dict]):
    """
    Pre-generate multiple commentaries for instant playback

    Body: [
        {"text": "Nice throw!", "quality": "great"},
        {"text": "Missed it!", "quality": "miss"}
    ]
    """
    if not cache_manager:
        raise HTTPException(status_code=503, detail="Cache not ready")

    results = []

    for item in items:
        text = item.get("text", "")
        quality = item.get("quality")

        if not text:
            continue

        # Check if already cached
        if cache_manager.get_cached(text):
            results.append({"text": text, "status": "cached"})
            continue

        # Generate and cache
        try:
            enhanced = jim_personality.enhance_text(text, quality)
            audio = await tts_engine.generate_audio(enhanced)
            cache_manager.cache_audio(text, audio)
            results.append({"text": text, "status": "generated"})
            logger.info(f"Pre-generated: {text[:50]}...")

        except Exception as e:
            logger.error(f"Failed to generate '{text}': {e}")
            results.append({"text": text, "status": "failed", "error": str(e)})

    return {
        "status": "complete",
        "results": results,
        "total_cached": cache_manager.get_cache_size()
    }

@app.get("/cache/stats")
async def cache_stats():
    """Get cache statistics"""
    if not cache_manager:
        raise HTTPException(status_code=503, detail="Cache not ready")

    return {
        "total_items": cache_manager.get_cache_size(),
        "cache_dir": str(settings.cache_dir)
    }

@app.delete("/cache/clear")
async def clear_cache():
    """Clear all cached audio"""
    if not cache_manager:
        raise HTTPException(status_code=503, detail="Cache not ready")

    try:
        cache_manager.clear_cache()
        return {"status": "success", "message": "Cache cleared"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
