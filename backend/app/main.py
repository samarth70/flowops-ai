from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.db import init_db
from app.api.routes_crm import router as crm_router
from app.api.routes_agent import router as agent_router
from app.api.routes_eval import router as eval_router

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="Autonomous Agentic CRM Deal Desk with HITL Governance, Langfuse Observability, and DeepEval evaluation."
)

# CORS middleware configured for development and production Vercel apps
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Permissive for easy cloud deployment across Vercel & local
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize tables and seed initial mock CRM deals
@app.on_event("startup")
def on_startup():
    init_db()

# Mount API Routers
app.include_router(crm_router)
app.include_router(agent_router)
app.include_router(eval_router)

@app.get("/")
def root():
    return {
        "status": "online",
        "service": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "docs": "/docs",
        "free_tier_status": {
            "groq_configured": settings.has_groq,
            "gemini_configured": settings.has_gemini,
            "langfuse_configured": settings.has_langfuse,
            "active_model": settings.GROQ_MODEL if settings.has_groq else "offline-enterprise-simulator"
        }
    }

@app.get("/health")
def health_check():
    return {"status": "healthy"}

@app.get("/api/debug-models")
def debug_models():
    groq_models = []
    gemini_models = []
    groq_err = None
    gemini_err = None

    if settings.has_groq:
        try:
            from groq import Groq
            client = Groq(api_key=settings.GROQ_API_KEY)
            models = client.models.list()
            groq_models = [m.id for m in models.data]
        except Exception as e:
            groq_err = str(e)

    if settings.has_gemini:
        try:
            import google.generativeai as genai
            genai.configure(api_key=settings.GEMINI_API_KEY)
            models = genai.list_models()
            gemini_models = [m.name for m in models if "generateContent" in getattr(m, "supported_generation_methods", [])]
        except Exception as e:
            gemini_err = str(e)

    return {
        "groq": {"models": groq_models, "error": groq_err},
        "gemini": {"models": gemini_models, "error": gemini_err}
    }
