import asyncio
import os
import json
import logging
import textwrap
import requests
from typing import List, Optional, Dict, Any
from pydantic import ValidationError
from env import HallucinationEnv
from models import Action

# Configure Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("AuditorInference")

# Environment Constraints (From Official Sample)
API_KEY = os.getenv("HF_TOKEN") or os.getenv("API_KEY")
API_BASE_URL = os.getenv("API_BASE_URL") or "https://proxy.hackathon.com/v1"
MODEL_NAME = os.getenv("MODEL_NAME") or "gpt-4o"

BENCHMARK = "hallucination_auditor"
MAX_STEPS = 1 # Hallucination auditing is a single-step decision
SUCCESS_SCORE_THRESHOLD = 0.6

# Logging Helpers per Official Sample
def log_start(task: str, env: str, model: str) -> None:
    print(f"[START] task={task} env={env} model={model}", flush=True)

def log_step(step: int, action: Any, reward: float, done: bool, error: Optional[str]) -> None:
    error_val = error if error else "null"
    done_val = str(done).lower()
    # Format according to sample spec
    print(
        f"[STEP] step={step} action={action} reward={reward:.2f} done={done_val} error={error_val}",
        flush=True,
    )

def log_end(success: bool, steps: int, score: float, rewards: List[float]) -> None:
    rewards_str = ",".join(f"{r:.2f}" for r in rewards)
    print(f"[END] success={str(success).lower()} steps={steps} score={score:.2f} rewards={rewards_str}", flush=True)

def get_model_message(obs: Any) -> str:
    """Manual request to ensure proxy compatibility."""
    url = f"{API_BASE_URL.rstrip('/')}/chat/completions"
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    data = {
        "model": MODEL_NAME,
        "messages": [
            {"role": "system", "content": "You are a hallucination auditor. Respond only in JSON."},
            {"role": "user", "content": f"Problem: {obs.question}\nAnswer: {obs.model_answer}\n\n"
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
        response = requests.post(url, headers=headers, json=data, timeout=30)
        if response.status_code != 200:
            logger.error(f"API Error ({response.status_code}): {response.text}")
        response.raise_for_status()
        result = response.json()
        return result["choices"][0]["message"]["content"]
    except Exception as e:
        logger.error(f"Model request failed: {e}")
        return "{}"

async def main() -> None:
    # Ensure keys exist as per strict rules
    if not API_KEY or not API_BASE_URL:
        # Fallback to local check if not provided (though validator will provide them)
        pass

    env = HallucinationEnv()
    all_task_rewards = []
    
    # We evaluate across the tasks registered in the environment (Easy, Medium, Hard)
    for i in range(3):
        task_name = f"hallucination_task_{i+1}"
        rewards: List[float] = []
        steps_taken = 0
        success = False
        
        log_start(task=task_name, env=BENCHMARK, model=MODEL_NAME)
        
        try:
            obs = await env.reset()
            done = False
            
            for step in range(1, MAX_STEPS + 1):
                raw_response = get_model_message(obs)
                
                try:
                    action_data = json.loads(raw_response)
                    action = Action(**action_data)
                    action_str = str(action.is_hallucination)
                except Exception as e:
                    # FALLBACK MUST INCLUDE ALL MANDATORY FIELDS
                    action = Action(
                        is_hallucination=False, 
                        confidence=0.0, 
                        risk_level="Low", 
                        recommended_action="Review",
                        reasoning=f"Parse error or API failure: {e}"
                    )
                    action_str = "Error"
                
                obs, reward, done, info = await env.step(action)
                
                rewards.append(reward)
                steps_taken = step
                
                log_step(step=step, action=action_str, reward=reward, done=done, error=None)
                
                if done:
                    break
            
            score = sum(rewards) / len(rewards) if rewards else 0.0
            all_task_rewards.append(score)
            success = score >= SUCCESS_SCORE_THRESHOLD
            
        finally:
            # log_end must always be called even on exception
            log_end(success=success, steps=steps_taken, score=score, rewards=rewards)

    avg_score = sum(all_task_rewards) / len(all_task_rewards) if all_task_rewards else 0.0
    print(f"\nFINAL REPRODUCIBLE BASELINE SCORE: {avg_score:.2f}")

if __name__ == "__main__":
    asyncio.run(main())
