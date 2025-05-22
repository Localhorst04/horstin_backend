from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path
import os

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)
BASE_DIR = Path("/home/localhorst/1projects/dump").resolve()

@app.get("/list")
def list_directory(path: str = ""):
    full_path = (BASE_DIR / path).resolve()

    # Security: Prevent directory traversal
    if not full_path.exists() or not full_path.is_dir() or BASE_DIR not in full_path.parents and full_path != BASE_DIR:
        raise HTTPException(status_code=404, detail="Invalid path")

    contents = []
    for entry in full_path.iterdir():
        contents.append({
            "name": entry.name,
            "type": "directory" if entry.is_dir() else "file",
            "downloadUrl": None if entry.is_dir() else f"/files/{(full_path.relative_to(BASE_DIR) / entry.name).as_posix()}"
        })

    return {"contents": contents}

@app.get("/files/{file_path:path}")
def download_file(file_path: str):
    full_path = (BASE_DIR / file_path).resolve()

    if not full_path.exists() or not full_path.is_file() or BASE_DIR not in full_path.parents:
        raise HTTPException(status_code=404, detail="File not found")

    return FileResponse(full_path, filename=full_path.name, media_type='application/octet-stream')
