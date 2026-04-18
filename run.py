from fastapi import FastAPI

app = FastAPI(title="SpiderShare")


@app.get("/health")
def health_check() -> dict[str, str]:
    return {"status": "ok"}
