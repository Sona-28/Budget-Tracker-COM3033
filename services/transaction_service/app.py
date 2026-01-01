from fastapi import FastAPI
from dotenv import load_dotenv

load_dotenv()

from services.transaction_service.api.v1 import transactions, analytics
from services.transaction_service.database.connection import engine
from services.transaction_service.models import transaction

# Create tables
transaction.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Transactions Service",
    version="v1",
    description="API for managing transactions and analytics"
)

# Routers
app.include_router(transactions.router, prefix="/api/v1/transactions", tags=["Transactions"])
app.include_router(analytics.router, prefix="/api/v1", tags=["Analytics"]) 

@app.get("/health", tags=["Health"])
def health():
    return {"service": "transactions", "status": "ok", "version": "v1"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="0.0.0.0", port=5002, reload=True, log_level="info")
