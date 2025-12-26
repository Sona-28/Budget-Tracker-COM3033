from fastapi import FastAPI
from app.database.connection import engine, Base
from app.models import transaction

app = FastAPI(title="Transactions Service")

Base.metadata.create_all(bind=engine)

@app.get("/health", tags=["Health"])
def health():
    return {
        "service": "transactions",
        "version": "v1",
        "status": "ok"
    }

from app.api.v1.transactions import router as transactions_router

app.include_router(transactions_router, prefix="/api/v1")
