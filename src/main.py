from dotenv import load_dotenv

from .api import register_routes
from .create_app import create_app
from .logging import LogLevels, configure_logging

configure_logging(LogLevels.info)

load_dotenv()

app = create_app()

register_routes(app)


@app.get("/health")
async def health():
    return {"status": "ok"}
