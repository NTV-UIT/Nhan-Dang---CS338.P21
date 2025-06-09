from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from apis.mapper_router import router as mapper_router
import os
import sys
sys.path.insert(0, os.path.join(os.environ['CONDA_PREFIX'], 'lib/python3.12/site-packages'))

# Create necessary directories
os.makedirs("templates", exist_ok=True)
os.makedirs("static", exist_ok=True)

app = FastAPI() 

# Add CORS middleware with all origins allowed
app.add_middleware(
    CORSMiddleware,
    # allow_origins=["*"],  # Allow all origins
    allow_origins=["http://127.0.0.1:5500"],
    allow_credentials=True,
    allow_methods=["*"],  # Allow all methods
    allow_headers=["*"],  # Allow all headers
    expose_headers=["*"]  # Expose all headers
)

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Include router
app.include_router(mapper_router)

@app.get("/")
async def root():
    return FileResponse("templates/index.html")

@app.get("/test")
async def test():
    return {"status": "ok", "message": "Server is running"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)