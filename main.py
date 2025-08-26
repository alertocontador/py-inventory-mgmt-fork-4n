from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import health, apis
from db.postgresql import connect_postgresql

app = FastAPI(
    title="Py Inventory Mgmt API",
    description="Inventory management is a critical excercise for any online business. In this challenge you will be implementing few core APIs for inventory management",
    version="1.0.0"
)


# Database connection on startup
@app.on_event("startup")
async def startup_event():
    await connect_postgresql()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure this properly for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(health.router, prefix="", tags=["health"])
app.include_router(apis.router, prefix="", tags=["apis"])

if __name__ == "__main__":
    import uvicorn
    import os
    
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", 8000))
    
    uvicorn.run(app, host=host, port=port)