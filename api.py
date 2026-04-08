from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from service import service
from typing import List, Dict, Any

app = FastAPI(
    title="AI Reliability & Risk Auditing System",
    description="Product-grade auditing service based on OpenEnv hallucination benchmark.",
    version="1.0.0"
)

class AuditRequest(BaseModel):
    question: str
    model_output: str

class AuditResponse(BaseModel):
    is_hallucination: bool
    confidence: float
    risk_level: str
    recommended_action: str
    score: float
    explanation: str

@app.get("/")
async def root():
    return {
        "message": "AI Reliability & Risk Auditing System is Online",
        "mode": "API",
        "status": "Ready for OpenEnv Evaluation",
        "endpoints": ["/reset", "/step", "/state", "/audit", "/logs"]
    }

@app.post("/audit", response_model=AuditResponse)
async def audit_endpoint(request: AuditRequest):
    """
    Endpoint to audit a single AI response for hallucinations.
    """
    try:
        result = service.audit(request.question, request.model_output)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/logs")
async def get_logs_endpoint():
    """
    Retrieve historical audit logs.
    """
    return service.get_logs()

@app.get("/health")
async def health_check():
    return {"status": "healthy", "engine": "OpenEnv-Hallucination-Auditor"}

# OpenEnv Compliance Endpoints
@app.post("/reset")
async def reset_endpoint():
    """Reset the environment and return the first observation."""
    return service.reset()

@app.post("/step")
async def step_endpoint(action: Dict[str, Any]):
    """Execute a step in the environment."""
    return service.step(action)

@app.get("/state")
async def state_endpoint():
    """Get the current state of the environment."""
    return service.state()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
