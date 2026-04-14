from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import router

app = FastAPI(title="AdPersonalize API")

# 🔥 VERY IMPORTANT — CORS FIX
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # ✅ allow ALL (for demo)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routes
app.include_router(router)


# Health check (VERY IMPORTANT for Render)
@app.get("/")
def root():
    return {"message": "Backend running 🚀"}