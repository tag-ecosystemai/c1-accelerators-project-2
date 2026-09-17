from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .routes.auth import router as auth_router
from .routes.candidates import router as candidates_router
from .routes.explanations import router as explanations_router
from .routes.jobs import router as jobs_router


app = FastAPI(
    title="TalentMatch AI API",
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(auth_router)
app.include_router(jobs_router)
app.include_router(candidates_router)
app.include_router(explanations_router)


@app.get("/health")
def health_check() -> dict[str, str]:
    return {
        "status": "ok",
        "message": "TalentMatch AI API is running!",
    }

