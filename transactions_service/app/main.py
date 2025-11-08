from fastapi import FastAPI
from app.api.v1.transactions import router as transactions_router

app = FastAPI(title="Transactions Microservice")

app.include_router(transactions_router)

@app.get("/")
def root():
    return {"message": "Transactions Service is running!"}

