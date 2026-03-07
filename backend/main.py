from fastapi import FastAPI
from backend.api.diagnostics_routes import router as diagnostics_router

app = FastAPI(
    title="FixMyInternet API",
    description="Network diagnostics API for detecting internet issues",
    version="1.0.0"
)

@app.get("/")
def home():
    return {"message": "FixMyInternet API is running"}

@app.get("/health")
def health_check():
    return {"status": "running"}

app.include_router(diagnostics_router)