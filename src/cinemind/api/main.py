from fastapi import FastAPI

from cinemind.api.routes import router
from cinemind.core.config import load_dotenv

load_dotenv()

app = FastAPI(
    title="Cinemind API",
    version="0.1.0",
    description="LLM-based grounded movie recommendation API",
)

app.include_router(router)
