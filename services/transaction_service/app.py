# services/transaction_service/app.py
from fastapi import FastAPI
from services.transaction_service.api.v1 import transactions

app = FastAPI(title="Transactions Service", version="v1")

# Include your transactions router
app.include_router(transactions.router, prefix="/api/v1")

# Health endpoint at root (optional)
@app.get("/health")
def health():
    return {"service": "transactions", "status": "ok", "version": "v1"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5002)

