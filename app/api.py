from fastapi import FastAPI
from datetime import datetime, timezone
from app.schemas import LogEvent
from app.redis_client import push_log
from app.db import init_db

app = FastAPI()


@app.on_event("startup")
def startup():
    init_db()
    print("API startup complete")


@app.post("/logs")
async def ingest_log(log: LogEvent):
    print("received request")

    event = log.dict()
    print("after dict():", event)

    event["timestamp"] = log.timestamp.isoformat()
    event["ingested_at"] = datetime.now(timezone.utc).isoformat()
    print("final event:", event)

    push_log(event)
    print("push_log completed")

    return {"status": "received"}