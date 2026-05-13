"""FastAPI application — serves all API endpoints (API-001 through API-007)."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.api.routes import intake, cases, human_review

app = FastAPI(title="Child Welfare Intake API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(intake.router, prefix="/intake", tags=["Intake"])
app.include_router(cases.router, prefix="/cases", tags=["Cases"])
app.include_router(human_review.router, prefix="/cases", tags=["Human Review"])


@app.get("/health")
def health():
    return {"status": "ok"}
