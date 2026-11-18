import json
import os
from datetime import datetime, timezone
from uuid import uuid4

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from redis.asyncio import Redis

app = FastAPI(title="Gaban Provos Control Plane", version="0.1.0")


class TaskRequest(BaseModel):
    title: str = Field(min_length=3, max_length=140)
    objective: str = Field(min_length=3, max_length=4000)
    risk_level: str = Field(default="low", pattern="^(low|medium|high)$")
    requires_approval: bool = True


def redis_client() -> Redis:
    return Redis.from_url(os.environ["REDIS_URL"], decode_responses=True)


@app.get("/api/health")
async def health() -> dict:
    client = redis_client()
    try:
        await client.ping()
        return {"status": "ok", "service": "control-plane"}
    finally:
        await client.aclose()


@app.post("/api/tasks", status_code=202)
async def create_task(request: TaskRequest) -> dict:
    task = {
        "id": str(uuid4()),
        "title": request.title,
        "objective": request.objective,
        "risk_level": request.risk_level,
        "requires_approval": request.requires_approval,
        "status": "awaiting_approval" if request.requires_approval else "queued",
        "owner": "hermes",
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    client = redis_client()
    try:
        await client.hset(f"task:{task['id']}", mapping={k: json.dumps(v) for k, v in task.items()})
        if not request.requires_approval:
            await client.lpush("dispatch:hermes", json.dumps(task))
    finally:
        await client.aclose()
    return task


@app.get("/api/tasks/{task_id}")
async def get_task(task_id: str) -> dict:
    client = redis_client()
    try:
        raw = await client.hgetall(f"task:{task_id}")
    finally:
        await client.aclose()
    if not raw:
        raise HTTPException(status_code=404, detail="Task not found")
    return {key: json.loads(value) for key, value in raw.items()}

