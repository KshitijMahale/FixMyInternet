from fastapi import FastAPI

app = FastAPI(
    title="FixMyInternet API",
    description="Network diagnostics API for detecting internet issues",
    version="1.0.0"
)


@app.get("/")
def home():
    return {
        "message": "FixMyInternet API is running"
    }


@app.get("/health")
def health_check():
    return {
        "status": "running"
    }