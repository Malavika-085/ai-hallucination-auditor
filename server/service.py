import json
import os
from datetime import datetime
from typing import Dict, Any, List
from openai import OpenAI
from .env import HallucinationEnv
from .models import Action, Observation, RiskLevel, RecommendedAction
from .tasks import grade_action, TASKS

class AuditService:
    def __init__(self):
        self.env = HallucinationEnv()
        self.log_file = "logs/audit_log.json"
        
        # Initialize OpenAI client with Validator Proxy credentials (STRICT ACCESS)
        self.api_base_url = os.environ["API_BASE_URL"]
        self.api_key = os.environ["API_KEY"]
        self.model_name = os.environ.get("MODEL_NAME", "gpt-4o")
        
        self.client = OpenAI(base_url=self.api_base_url, api_key=self.api_key)
        
        os.makedirs("logs", exist_ok=True)
        if not os.path.exists(self.log_file):
            with open(self.log_file, "w") as f:
                json.dump([], f)

    def _get_auditor_response(self, question: str, model_answer: str) -> Action:
        """
        Calls the live LLM proxy to audit the hallucination.
        This ensures the LiteLLM proxy observes the API traffic.
        """
        try:
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=[
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
                temperature=0
            )
            
            content = response.choices[0].message.content
            action_data = json.loads(content)
            return Action(**action_data)
            
        except Exception as e:
            print(f"API Error in AuditService: {e}")
            # Fallback to a safe 'failed' action if the API is down
            return Action(
                is_hallucination=False,
                confidence=0.0,
                risk_level=RiskLevel.LOW,
                recommended_action=RecommendedAction.REVIEW,
                reasoning=f"Audit failed due to technical error: {str(e)}"
            )

    def audit(self, question: str, model_answer: str) -> Dict[str, Any]:
        """
        Performs an audit, calculates score if ground truth is available, and logs result.
        """
        action = self._get_auditor_response(question, model_answer)
        
        # Try to find a matching predefined task for reward calculation
        score = 0.0
        details = "Custom input - no ground truth for scoring"
        
        for task in TASKS:
            if task["question"] == question and task["model_answer"] == model_answer:
                score = grade_action(action, task)
                details = f"Matched predefined task: {task['difficulty']} level"
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
    def reset(self) -> Observation:
        return self.env.reset()

    def step(self, action_dict: Dict[str, Any]) -> Dict[str, Any]:
        # Convert dict to Action model
        action = Action(**action_dict)
        obs, reward, done, info = self.env.step(action)
        return {
            "observation": obs.dict(),
            "reward": reward,
            "done": done,
            "info": info
        }

    def state(self) -> Dict[str, Any]:
        return self.env.state()

service = AuditService()
