import builtins
import torch
import numpy as np
import io
from scipy.io.wavfile import write
import logging
from pathlib import Path
from app.tts_base import BaseTTSEngine

# Monkeypatch input to auto-accept TTS license
def _auto_accept_input(prompt=""):
    # Always return 'y' to accept TTS license automatically
    return "y"
builtins.input = _auto_accept_input

from TTS.api import TTS

logger = logging.getLogger(__name__)

class XTTSEngine(BaseTTSEngine):
    """Coqui XTTS-based TTS engine for GPU/CPU"""

    def __init__(self, model_name: str, device: str = "cuda", speaker_wav: str = None):
        super().__init__(model_name, device, speaker_wav)

        # Check if CUDA is actually available
        self.device = device if torch.cuda.is_available() and device == "cuda" else "cpu"

        if device == "cuda" and self.device == "cpu":
            logger.warning("CUDA requested but not available, falling back to CPU")

        logger.info(f"Initializing XTTS on {self.device}")

        # Load model
        self.tts = TTS(model_name).to(self.device)
        self.sample_rate = 22050

        logger.info(f"✅ XTTS model loaded: {model_name}")
        if self.speaker_wav:
            logger.info(f"✅ Using voice clone: {self.speaker_wav}")
        else:
            logger.info("ℹ️  Using default speaker (no voice clone)")

    def is_gpu_available(self) -> bool:
        """Check if GPU is being used"""
        return torch.cuda.is_available() and self.device == "cuda"

    async def generate_audio(self, text: str, speed: float = 0.95) -> bytes:
        """
        Generate audio from text using XTTS

        Args:
            text: Text to synthesize
            speed: Speech rate (0.8-1.2, lower = slower/more drunk)

        Returns:
            WAV audio as bytes
        """
        try:
            # Generate audio array
            if self.speaker_wav:
                # Use voice cloning
                wav = self.tts.tts(
                    text=text,
                    speaker_wav=self.speaker_wav,
                    language="en",
                    speed=speed
                )
            else:
                # Use default speaker - XTTS requires either speaker_wav or speaker name
                # Using a sample voice from the model
                wav = self.tts.tts(
                    text=text,
                    language="en",
                    speed=speed,
                    speaker="Claribel Dervla"  # Default XTTS sample speaker
                )

            # Convert to WAV bytes
            wav_array = np.array(wav)

            # Create WAV file in memory
            buffer = io.BytesIO()
            write(buffer, self.sample_rate, wav_array.astype(np.float32))
            buffer.seek(0)

            return buffer.read()

        except Exception as e:
            logger.error(f"Error generating audio: {e}")
            raise

    def get_voice_info(self) -> dict:
        """Get information about loaded voice"""
        return {
            "engine": "xtts",
            "model": self.tts.model_name,
            "device": self.device,
            "speaker_wav": self.speaker_wav,
            "sample_rate": self.sample_rate
        }
