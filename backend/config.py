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
    renderer_url: str | None = None
    renderer_dedicated: bool = False
    workflow_root: Path | None = None
    reference_root: Path | None = None
    render_output_root: Path | None = None
    visuals_parse_failed: bool = False
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
        for name in ("workflow_root", "reference_root", "render_output_root"):
            raw = env.get(f"INCANTA_{name.upper()}")
            if raw is not None:
                try:
                    if not raw or "\0" in raw:
                        raise ValueError
                    # Keep the path spelling so visual file access can reject symlinks.
                    path = Path(raw).expanduser()
                    values[name] = path if path.is_absolute() else ROOT / path
                except (ValueError, RuntimeError):
                    values["visuals_parse_failed"] = True
        values["renderer_url"] = env.get("INCANTA_RENDERER_URL")
        dedicated = env.get("INCANTA_RENDERER_DEDICATED", "0")
        values["renderer_dedicated"] = dedicated == "1"
        if dedicated not in {"0", "1"}:
            values["visuals_parse_failed"] = True
        if "INCANTA_HOST" in env:
            values["host"] = env["INCANTA_HOST"]
        for name in ["port", "context_length", "gpu_layers", "threads"]:
            if f"INCANTA_{name.upper()}" in env:
                try:
                    values[name] = int(env[f"INCANTA_{name.upper()}"])
                except (ValueError, TypeError):
                    failed = True
        return cls(**values, parse_failed=failed)
