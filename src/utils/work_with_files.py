import shutil
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
SERVERS_DIR = BASE_DIR / "servers"


def get_server_dir(server_name: str) -> Path:
    server_path = SERVERS_DIR / server_name
    server_path.mkdir(parents=True, exist_ok=True)
    return server_path


def ensure_server_dir(server_name: str) -> Path:
    server_path = SERVERS_DIR / server_name
    server_path.mkdir(parents=True, exist_ok=True)
    return server_path


def remove_server_dir(server_name: str) -> None:
    server_path = SERVERS_DIR / server_name
    if server_path.exists():
        shutil.rmtree(server_path)


__all__ = ["get_server_dir", "ensure_server_dir", "remove_server_dir"]
