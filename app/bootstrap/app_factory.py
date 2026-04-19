from fastapi import FastAPI

def create_app():
    app = FastAPI(title="SpiderShare")

    @app.get("/health")
    def health_check() -> dict[str, str]:
        return {"status": "ok"}
    
    return app