from pydantic_settings import BaseSettings
from typing import List, Literal
import platform
import os

class Settings(BaseSettings):
    # Server settings
    server_host: str = "0.0.0.0"
    server_port: int = 8000
    log_level: str = "INFO"

    # TTS Engine settings
    tts_engine: Literal["auto", "xtts", "mlx"] = "auto"  # auto-detect or force specific engine
    tts_model: str = "tts_models/multilingual/multi-dataset/xtts_v2"
    tts_device: str = "cpu"  # 'cpu' or 'cuda' (for XTTS)
    speaker_wav: str = "/app/voices/jim_voice.wav"

    @property
    def selected_engine(self) -> str:
        """Auto-detect the best TTS engine for the platform"""
        if self.tts_engine != "auto":
            return self.tts_engine

        # Check if running on macOS with Apple Silicon
        if platform.system() == "Darwin":
            # Check for Apple Silicon (arm64)
            if platform.machine() == "arm64":
                return "mlx"

        # Default to XTTS for other platforms
        return "xtts"

    # Cache settings
    cache_dir: str = "/app/cache/pregenerated"
    pregenerate_on_startup: bool = True

    # SSL settings
    ssl_cert_path: str = "/app/certs/cert.pem"
    ssl_key_path: str = "/app/certs/key.pem"

    # CORS
    cors_origins: List[str] = ["*"]

    class Config:
        env_file = ".env"
        case_sensitive = False

settings = Settings()
