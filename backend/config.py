"""Local settings; importing this module never reads assets or loads inference."""
from dataclasses import dataclass
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LOOPBACK = {"127.0.0.1", "::1", "localhost"}


@dataclass(frozen=True)
class Settings:
    model_path: Path = ROOT / "models/Nous-Hermes-2-Mistral-7B-DPO.Q4_K_S.gguf"
    personality_path: Path = ROOT / "backend/personalities/celeste.json"
    data_dir: Path = ROOT / "chat_histories"
    database_path: Path | None = None
    import_path: Path | None = None
    host: str = "127.0.0.1"
    port: int = 5001
    context_length: int = 4096
    gpu_layers: int = 0
    threads: int = 8
    parse_failed: bool = False

    @property
    def valid(self):
        return (
            not self.parse_failed and self.host in LOOPBACK
            and 1 <= self.port <= 65535 and 128 <= self.context_length <= 131072
            and -1 <= self.gpu_layers <= 1000 and 1 <= self.threads <= 256
        )

    @classmethod
    def from_env(cls, environ=None):
        env = os.environ if environ is None else environ
        values = {}
        failed = False
        for name in ["model_path", "personality_path", "data_dir", "database_path", "import_path"]:
            if f"INCANTA_{name.upper()}" in env:
                try:
                    raw = env[f"INCANTA_{name.upper()}"]
                    if not raw or "\0" in raw:
                        raise ValueError
                    path = Path(raw).expanduser()
                    values[name] = (ROOT / path).resolve() if not path.is_absolute() else path.resolve()
                except (OSError, ValueError, RuntimeError):
                    failed = True
        if "INCANTA_HOST" in env:
            values["host"] = env["INCANTA_HOST"]
        for name in ["port", "context_length", "gpu_layers", "threads"]:
            if f"INCANTA_{name.upper()}" in env:
                try:
                    values[name] = int(env[f"INCANTA_{name.upper()}"])
                except (ValueError, TypeError):
                    failed = True
        return cls(**values, parse_failed=failed)
