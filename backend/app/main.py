from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
# from app.apis.latent_optimization_router import router as latent_optimization_router
from apis.mapper_router import router as mapper_router
# from app.apis.global_direction_router import router as global_direction_router

app = FastAPI() 

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# app.include_router(latent_optimization_router)
app.include_router(mapper_router)
# app.include_router(global_direction_router)

@app.get("/")
async def root():
    return {"message": "Xin chao"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)