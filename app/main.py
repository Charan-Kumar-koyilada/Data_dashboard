from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.db import init_db
from app.routes.user_routes import router as user_router
from app.routes.upload_routes import router as upload_router

# ✅ Create the FastAPI app only once
app = FastAPI(title="DataViz Dashboard")

# ✅ Enable CORS (so frontend can call APIs)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # change this to your frontend URL in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ✅ Include the routers
app.include_router(user_router)
app.include_router(upload_router)

# ✅ Initialize database at startup
@app.on_event("startup")
def on_startup():
    init_db()

# ✅ Root endpoint
@app.get("/")
def root():
    return {"message": "Backend is running successfully 🚀"}
