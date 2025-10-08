import hashlib
import pickle
from pathlib import Path
import logging
from typing import Optional

logger = logging.getLogger(__name__)

class AudioCacheManager:
    """Manages pre-generated and cached audio"""

    def __init__(self, tts_engine, jim_personality, cache_dir: str = "cache/pregenerated"):
        self.tts_engine = tts_engine
        self.jim_personality = jim_personality
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)

        # In-memory cache for fastest access
        self.memory_cache = {}

        # Load existing cache from disk
        self._load_disk_cache()

    def _get_cache_key(self, text: str) -> str:
        """Generate cache key from text"""
        return hashlib.md5(text.encode()).hexdigest()

    def _load_disk_cache(self):
        """Load cached audio files from disk into memory"""
        logger.info("Loading cached audio from disk...")
        count = 0

        for cache_file in self.cache_dir.glob("*.pkl"):
            try:
                with open(cache_file, 'rb') as f:
                    data = pickle.load(f)
                    self.memory_cache[data['key']] = data['audio']
                    count += 1
            except Exception as e:
                logger.error(f"Error loading cache file {cache_file}: {e}")

        logger.info(f"📦 Loaded {count} cached audio files")

    def get_cached(self, text: str) -> Optional[bytes]:
        """Get cached audio for text"""
        key = self._get_cache_key(text)
        return self.memory_cache.get(key)

    def cache_audio(self, text: str, audio_bytes: bytes):
        """Cache audio in memory and on disk"""
        key = self._get_cache_key(text)

        # Store in memory
        self.memory_cache[key] = audio_bytes

        # Store on disk
        cache_file = self.cache_dir / f"{key}.pkl"
        try:
            with open(cache_file, 'wb') as f:
                pickle.dump({'key': key, 'text': text, 'audio': audio_bytes}, f)
        except Exception as e:
            logger.error(f"Error caching to disk: {e}")

    def get_cache_size(self) -> int:
        """Get number of cached items"""
        return len(self.memory_cache)

    def clear_cache(self):
        """Clear all cached audio"""
        self.memory_cache.clear()
        for cache_file in self.cache_dir.glob("*.pkl"):
            try:
                cache_file.unlink()
            except Exception as e:
                logger.error(f"Error deleting cache file: {e}")
        logger.info("Cache cleared")

    async def pregenerate_common_phrases(self):
        """Pre-generate frequently used phrases"""
        common_phrases = [
            "Nice throw!",
            "Ohhh, that's a miss!",
            "Triple twenty! Amazing!",
            "Bullseye! Holy shit!",
            "You suck at this!",
            "Are you even trying?",
            "*burps* Sorry about that...",
            "Next player!",
            "Game over!",
            "What a comeback!",
        ]

        generated = 0
        for phrase in common_phrases:
            if not self.get_cached(phrase):
                logger.info(f"Pre-generating: {phrase}")
                enhanced = self.jim_personality.enhance_text(phrase)
                audio = await self.tts_engine.generate_audio(enhanced)
                self.cache_audio(phrase, audio)
                generated += 1

        logger.info(f"✅ Pre-generated {generated} new phrases ({len(common_phrases) - generated} were cached)")
