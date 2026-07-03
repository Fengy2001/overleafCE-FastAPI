from fastapi import FastAPI, UploadFile, HTTPException, Form
from contextlib import asynccontextmanager
import asyncio

@asynccontextmanager
async def lifespan(app : FastAPI):
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
        "docker", "exec", "-i", "sharelatex",
        "node", "modules/custom-scripts/create-project.mjs",
        owner_email, project_name,
        stdin=asyncio.subprocess.PIPE,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    stdout, stderr = await proc.communicate(input=zip_bytes)
    if proc.returncode != 0:
        raise HTTPException(500, stderr.decode())

    return {"result": stdout.decode().strip()}