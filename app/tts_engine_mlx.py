import numpy as np
import io
from scipy.io.wavfile import write
import logging
import tempfile
from pathlib import Path
from app.tts_base import BaseTTSEngine

logger = logging.getLogger(__name__)

class MLXEngine(BaseTTSEngine):
    """MLX-Audio TTS engine optimized for Apple Silicon"""

    def __init__(self, model_name: str = "mlx-community/csm-1b", device: str = "mps", speaker_wav: str = None):
        super().__init__(model_name, device, speaker_wav)

        logger.info(f"Initializing MLX-Audio TTS on Apple Silicon")

        # Import MLX-Audio (only available on macOS)
        try:
            from mlx_audio.tts.generate import generate_audio
            self.generate_func = generate_audio
        except ImportError as e:
            logger.error("MLX-Audio not found. Install with: pip install mlx-audio")
            raise ImportError("MLX-Audio is required for Apple Silicon. Run: pip install mlx-audio") from e

        self.model_name = model_name
        self.sample_rate = 24000  # MLX-Audio CSM default sample rate

        logger.info(f"✅ MLX-Audio model loaded: {model_name}")
        if self.speaker_wav:
            logger.info(f"✅ Using voice clone: {self.speaker_wav}")
        else:
            logger.warning("⚠️  No speaker_wav provided - MLX CSM works best with reference audio")

    def is_gpu_available(self) -> bool:
        """Check if Apple Silicon acceleration is available"""
        try:
            import platform
            return platform.system() == "Darwin" and platform.machine() == "arm64"
        except:
            return False

    async def generate_audio(self, text: str, speed: float = 0.95) -> bytes:
        """
        Generate audio from text using MLX-Audio CSM

        Args:
            text: Text to synthesize
            speed: Speech rate (0.8-1.2, lower = slower/more drunk)

        Returns:
            WAV audio as bytes
        """
        try:
            # Create a temporary directory for MLX-Audio output
            with tempfile.TemporaryDirectory() as temp_dir:
                temp_path = Path(temp_dir)

                # MLX-Audio expects file paths for output
                output_prefix = str(temp_path / "output")

                # Generate audio using MLX-Audio
                logger.debug(f"Generating audio with MLX-Audio: {text[:50]}...")

                # Call MLX-Audio generation function
                # Note: generate_audio writes to file and returns None
                self.generate_func(
                    text=text,
                    model_path=self.model_name,  # "mlx-community/csm-1b"
                    ref_audio=self.speaker_wav if self.speaker_wav else None,
                    speed=speed,
                    file_prefix=output_prefix,
                    audio_format="wav",
                    join_audio=True,
                    verbose=False,
                    play=False  # Don't play audio, just generate
                )

                # Find the generated WAV file - MLX-Audio appends _0, _1, etc
                output_file = temp_path / "output_0.wav"

                if not output_file.exists():
                    # Try without suffix
                    output_file = temp_path / "output.wav"

                if not output_file.exists():
                    # Try to find any WAV file generated
                    wav_files = list(temp_path.glob("*.wav"))
                    if wav_files:
                        output_file = wav_files[0]
                        logger.debug(f"Using generated file: {output_file.name}")
                    else:
                        raise FileNotFoundError(f"MLX-Audio did not generate output file. Expected at {temp_path / 'output_0.wav'}")

                # Read the WAV file and return as bytes
                with open(output_file, 'rb') as f:
                    audio_bytes = f.read()

                logger.debug(f"Generated {len(audio_bytes)} bytes of audio")
                return audio_bytes

        except Exception as e:
            logger.error(f"Error generating audio with MLX: {e}")
            logger.exception("Full traceback:")
            raise

    def get_voice_info(self) -> dict:
        """Get information about loaded voice"""
        return {
            "engine": "mlx",
            "model": self.model_name,
            "device": "Apple Silicon (MPS)",
            "speaker_wav": self.speaker_wav,
            "sample_rate": self.sample_rate
        }
