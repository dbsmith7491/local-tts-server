"""
TTS Engine Factory
Selects the appropriate TTS engine based on platform and configuration
"""
import logging
from app.tts_base import BaseTTSEngine
from app.config import settings

logger = logging.getLogger(__name__)

def create_tts_engine(
    model_name: str = None,
    device: str = None,
    speaker_wav: str = None
) -> BaseTTSEngine:
    """
    Factory function to create the appropriate TTS engine

    Args:
        model_name: Model identifier (optional, uses settings default)
        device: Device to run on (optional, uses settings default)
        speaker_wav: Path to reference voice sample (optional, uses settings default)

    Returns:
        Appropriate TTS engine instance
    """
    # Use settings defaults if not provided
    model_name = model_name or settings.tts_model
    device = device or settings.tts_device
    speaker_wav = speaker_wav or settings.speaker_wav

    engine_type = settings.selected_engine
    logger.info(f"Creating TTS engine: {engine_type}")

    if engine_type == "mlx":
        from app.tts_engine_mlx import MLXEngine
        return MLXEngine(
            model_name="mlx-community/csm-1b",
            device="mps",
            speaker_wav=speaker_wav
        )
    elif engine_type == "xtts":
        from app.tts_engine_xtts import XTTSEngine
        return XTTSEngine(
            model_name=model_name,
            device=device,
            speaker_wav=speaker_wav
        )
    else:
        raise ValueError(f"Unknown engine type: {engine_type}")


# Backwards compatibility wrapper
class TTSEngine:
    """Legacy wrapper - use create_tts_engine() instead"""
    def __new__(cls, *args, **kwargs):
        logger.warning("TTSEngine class is deprecated, use create_tts_engine() instead")
        return create_tts_engine(*args, **kwargs)
