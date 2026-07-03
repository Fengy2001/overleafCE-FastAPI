from fastapi import FastAPI, UploadFile, HTTPException, Form
from contextlib import asynccontextmanager
import asyncio
import json

@asynccontextmanager
async def lifespan(app : FastAPI):
    with open("./secrets/secret.json") as file:
        data = json.load(file)
    app.state.container_name = data["container_name"]
    app.state.mjs_script = data["mjs-script"]
    yield
    

app = FastAPI(lifespan=lifespan)

@app.post("/create-project")
async def create_project(
        owner_email: str = Form(...),
        project_name: str = Form(...),
        zip_file: UploadFile = ...,
    ):

    zip_bytes = await zip_file.read()
    proc = await asyncio.create_subprocess_exec(
        "docker", "exec", "-i", app.state.container_name,
        "node", app.state.mjs_script,
        owner_email, project_name,
        stdin=asyncio.subprocess.PIPE,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    stdout, stderr = await proc.communicate(input=zip_bytes)
    if proc.returncode != 0:
        raise HTTPException(500, stderr.decode())

    return {"result": stdout.decode().strip()}