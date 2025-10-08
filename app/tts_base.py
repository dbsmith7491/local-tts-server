from abc import ABC, abstractmethod
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

class BaseTTSEngine(ABC):
    """Abstract base class for TTS engines"""

    def __init__(self, model_name: str, device: str = "cpu", speaker_wav: str = None):
        """
        Initialize TTS engine

        Args:
            model_name: Model identifier
            device: Device to run on ('cpu', 'cuda', 'mps', etc.)
            speaker_wav: Path to reference voice sample for cloning
        """
        self.model_name = model_name
        self.device = device
        self.speaker_wav = speaker_wav

        # Validate speaker wav
        if speaker_wav and not Path(speaker_wav).exists():
            logger.warning(f"Speaker wav not found: {speaker_wav}")
            logger.warning("Will use default speaker instead")
            self.speaker_wav = None

    @abstractmethod
    async def generate_audio(self, text: str, speed: float = 0.95) -> bytes:
        """
        Generate audio from text

        Args:
            text: Text to synthesize
            speed: Speech rate (0.8-1.2, lower = slower/more drunk)

        Returns:
            WAV audio as bytes
        """
        pass

    @abstractmethod
    def is_gpu_available(self) -> bool:
        """Check if GPU/acceleration is available"""
        pass

    @abstractmethod
    def get_voice_info(self) -> dict:
        """Get information about loaded voice"""
        pass

    @property
    def engine_name(self) -> str:
        """Return the name of this engine"""
        return self.__class__.__name__
