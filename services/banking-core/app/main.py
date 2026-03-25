import os
from dotenv import load_dotenv
from fastapi import FastAPI
import uvicorn
load_dotenv()

from app.db.migrations.session import engine, Base
from app.models.account import Account
from app.models.transaction import Transaction
from app.api.v1.endpoints import transfer, accounts, transactions

Base.metadata.create_all(bind=engine)

APP_NAME = os.getenv("APP_NAME")
APP_ENV = os.getenv("APP_ENV", "development")
APP_PORT = int(os.getenv("APP_PORT", 8002))
APP_RELOAD = os.getenv("APP_RELOAD")


def _should_enable_reload() -> bool:
    if APP_RELOAD is not None:
        return APP_RELOAD.strip().lower() == "true"

    # Git Bash on Windows can fail with WatchFiles named-pipe permissions.
    if os.name == "nt" and os.getenv("MSYSTEM"):
        return False

    return APP_ENV == "development"

app = FastAPI(title=APP_NAME)


@app.get("/health")
def health():
    return {
        "service": APP_NAME,
        "env": APP_ENV,
        "status": "UP"
    }


app.include_router(
    transfer.router,
    prefix="/transfers",
    tags=["Transfers"]
)



app.include_router(
    accounts.router,
    prefix="/accounts",
    tags=["Accounts"]
)

app.include_router(
    transactions.router,
    prefix="/transactions",
    tags=["Transactions"]
)

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=APP_PORT,
        reload=_should_enable_reload()
    )
