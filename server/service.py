import json
import os
import requests
from datetime import datetime
from typing import Dict, Any, List
# Importer from root
import sys
from pathlib import Path
root_path = str(Path(__file__).parent.parent)
if root_path not in sys.path:
    sys.path.append(root_path)

from env import HallucinationEnv
from models import Action, Observation, RiskLevel, RecommendedAction
from tasks import grade_action, TASKS

class AuditService:
    def __init__(self):
        self.env = HallucinationEnv()
        self.log_file = "logs/audit_log.json"
        
        # Pull config with fallbacks
        self.api_base_url = os.environ.get("API_BASE_URL", "https://proxy.hackathon.com/v1").rstrip("/")
        self.api_key = os.environ.get("API_KEY", "")
        self.model_name = os.environ.get("MODEL_NAME", "gpt-4o")
        
        os.makedirs("logs", exist_ok=True)
        if not os.path.exists(self.log_file):
            with open(self.log_file, "w") as f:
                json.dump([], f)

    async def _get_auditor_response(self, question: str, model_answer: str) -> Action:
        """
        Calls the live LLM proxy using raw requests.
        """
        url = f"{self.api_base_url}/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        data = {
            "model": self.model_name,
            "messages": [
                {"role": "system", "content": "You are a hallucination auditor. Respond only in JSON."},
                {"role": "user", "content": f"Problem: {question}\nAnswer: {model_answer}\n\n"
                                            "Decision Format:\n"
                                            "{\n"
                                            "  \"is_hallucination\": boolean,\n"
                                            "  \"confidence\": float (0-1),\n"
                                            "  \"risk_level\": \"Critical\" | \"High\" | \"Medium\" | \"Low\",\n"
                                            "  \"recommended_action\": \"Redact\" | \"Verify\" | \"Review\",\n"
                                            "  \"reasoning\": string\n"
                                            "}"}
            ],
            "temperature": 0
        }
        
        try:
            # Note: In a production async environment, we would use httpx.
            # But for this auditor, requests with timeout is acceptable.
            response = requests.post(url, headers=headers, json=data, timeout=30)
            response.raise_for_status()
            
            result = response.json()
            content = result["choices"][0]["message"]["content"]
            action_data = json.loads(content)
            return Action(**action_data)
            
        except Exception as e:
            print(f"API Error in AuditService: {e}")
            return Action(
                is_hallucination=False,
                confidence=0.0,
                risk_level=RiskLevel.LOW,
                recommended_action=RecommendedAction.REVIEW,
                reasoning=f"Audit failed due to technical error: {str(e)}"
            )

    async def audit(self, question: str, model_answer: str) -> Dict[str, Any]:
        """
        Performs an audit (Async).
        """
        action = await self._get_auditor_response(question, model_answer)
        
        # Try to find a matching predefined task for reward calculation
        score = 0.0
        
        for task in TASKS:
            if task["question"] == question and task["model_answer"] == model_answer:
                score = grade_action(action, task)
                break
        
        result = {
            "is_hallucination": action.is_hallucination,
            "confidence": action.confidence,
            "risk_level": action.risk_level.value,
            "recommended_action": action.recommended_action.value,
            "score": score,
            "explanation": action.reasoning,
            "timestamp": datetime.now().isoformat()
        }
        
        self._log_audit(question, model_answer, result)
        return result

    def _log_audit(self, question: str, model_answer: str, result: Dict[str, Any]):
        try:
            with open(self.log_file, "r") as f:
                logs = json.load(f)
            
            logs.append({
                "input": {"question": question, "model_answer": model_answer},
                "output": result,
            })
            
            with open(self.log_file, "w") as f:
                json.dump(logs, f, indent=4)
        except Exception as e:
            print(f"Logging error: {e}")

    def get_logs(self) -> List[Dict[str, Any]]:
        with open(self.log_file, "r") as f:
            return json.load(f)

    # OpenEnv Spec Compliance Endpoints
    async def reset(self) -> Observation:
        return await self.env.reset()

    async def step(self, action_dict: Dict[str, Any]) -> Dict[str, Any]:
        action = Action(**action_dict)
        obs, reward, done, info = await self.env.step(action)
        return {
            "observation": obs.dict(),
            "reward": reward,
            "done": done,
            "info": info
        }

    def state(self) -> Dict[str, Any]:
        return self.env.state()

service = AuditService()
