from fastapi import FastAPI

app = FastAPI(title="URL Shortener")


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/")
def root():
    return {"message": "URL shortener is running"}
