from fastapi import FastAPI

app = FastAPI(title="Helpdesk-AI API")

@app.get("/ping")
async def ping():
    return {"status": "ok"}
