from dotenv import load_dotenv
load_dotenv()                    # ← must be first, before everything else


from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes import router


app = FastAPI(title="AdPersonalize API")

# ✅ CORS — allows your Vite frontend (localhost:5173) to call the backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://ai-cro-assistant.vercel.app",   # Vite dev server
        
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)