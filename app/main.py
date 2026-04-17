from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core import APP_NAME
from app.database import engine, Base
from app.routes.income import router as income_router  # add this import
from app.routes.transactions import router as transactions_router
from app.routes.balances import router as balances_router
import app.models  # ensures all models are registered

# ── Create all tables on startup (safe — skips existing tables) ──
Base.metadata.create_all(bind=engine)

# ── Initialise the FastAPI app ───────────────────────────────────
app = FastAPI(
    title=APP_NAME,
    description="A personal finance tracker with rule-based auto-allocation.",
    version="0.1.0"
)

# ── CORS Middleware ──────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # tightened later when frontend URL is known
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(income_router)
app.include_router(transactions_router)
app.include_router(balances_router)

# ── Health check ─────────────────────────────────────────────────
@app.get("/", tags=["Health"])
def root():
    return {
        "app": APP_NAME,
        "status": "running",
        "version": "0.1.0"
    }

@app.get("/health", tags=["Health"])
def health():
    return {"status": "ok"}