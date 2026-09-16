from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List, Dict, Any
from app.db import get_db
from app.models import EvaluationRun
from evaluation.run_evals import run_evaluation_suite

router = APIRouter(prefix="/api/eval", tags=["Evaluation Suite"])

@router.get("/runs")
def list_eval_runs(db: Session = Depends(get_db)):
    runs = db.query(EvaluationRun).order_by(EvaluationRun.created_at.desc()).all()
    return [run.to_dict() for run in runs]

@router.get("/runs/latest")
def get_latest_eval(db: Session = Depends(get_db)):
    latest = db.query(EvaluationRun).order_by(EvaluationRun.created_at.desc()).first()
    if not latest:
        # Run one immediately if none exists
        latest = run_evaluation_suite()
    return latest.to_dict()

@router.post("/trigger")
def trigger_eval(model_name: str = "Groq Llama-3.3-70B"):
    run = run_evaluation_suite(model_override=model_name)
    return {
        "status": "completed",
        "message": f"Successfully evaluated golden benchmark on {model_name}",
        "run": run.to_dict()
    }
