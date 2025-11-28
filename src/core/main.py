from fastapi import FastAPI
import uvicorn
from src.api.router import router as api_router

app = FastAPI()

app.include_router(api_router)


if __name__ == "__main__":
    uvicorn.run("src.core.main:app", host="127.0.0.1", port=8000, reload=True)