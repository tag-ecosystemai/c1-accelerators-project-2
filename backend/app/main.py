from fastapi import FastAPI

from .routes.auth import router as auth_router
from .routes.jobs import router as jobs_router


app = FastAPI(title="TalentMatch AI API")

app.include_router(auth_router)
app.include_router(jobs_router)


@app.get("/health")
def health_check():
    return {
        "status": "ok",
        "message": "TalentMatch AI API is running!",
    }