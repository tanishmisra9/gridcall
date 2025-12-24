"""
Gridcall Backend API
FastAPI server for F1 prediction game
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api import races, predictions, users, grids
from database.connection import init_db

app = FastAPI(
    title="Gridcall API",
    description="F1 Prediction Game Backend",
    version="0.1.0"
)

# CORS middleware to allow frontend to communicate
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Next.js default port
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize database on startup
@app.on_event("startup")
async def startup_event():
    init_db()

# Include routers
app.include_router(races.router, prefix="/api/races", tags=["races"])
app.include_router(predictions.router, prefix="/api/predictions", tags=["predictions"])
app.include_router(users.router, prefix="/api/users", tags=["users"])
app.include_router(grids.router, prefix="/api/grids", tags=["grids"])

@app.get("/")
async def root():
    return {
        "message": "Gridcall API",
        "version": "0.1.0",
        "docs": "/docs"
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
