from fastapi import FastAPI
from dotenv import load_dotenv

load_dotenv()

from services.transaction_service.api.v1 import transactions, analytics

app = FastAPI(
    title="Transactions Service",
    version="v1"
)

# Core APIs
app.include_router(transactions.router, prefix="/api/v1")
app.include_router(analytics.router, prefix="/api/v1")

@app.get("/health")
def health():
    return {
        "service": "transactions",
        "status": "ok",
        "version": "v1"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5002)
