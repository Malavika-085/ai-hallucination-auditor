import asyncio
import os
import json
import logging
import textwrap
from typing import List, Optional, Dict, Any
from openai import OpenAI
from pydantic import ValidationError
from env import HallucinationEnv
from models import Action

# Configure Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("AuditorInference")

# 1. Read Environment Variables with Defaults (MANDATORY per Guidelines)
API_BASE_URL = os.getenv("API_BASE_URL", "https://proxy.hackathon.com/v1")
MODEL_NAME = os.getenv("MODEL_NAME", "gpt-4o")
HF_TOKEN = os.getenv("HF_TOKEN")

if HF_TOKEN is None:
    # We use a placeholder for local testing, but it is mandatory in the Space
    HF_TOKEN = os.getenv("API_KEY", "dummy_token")

# 2. Initialize OpenAI Client (MANDATORY: No direct HTTP calls)
client = OpenAI(
    base_url=API_BASE_URL,
    api_key=HF_TOKEN
)

BENCHMARK = "hallucination_auditor"
MAX_STEPS = 1 
SUCCESS_SCORE_THRESHOLD = 0.6

# Logging Helpers per Official Format
def log_start(task: str, env: str, model: str) -> None:
    print(f"[START] task={task} env={env} model={model}", flush=True)

def log_step(step: int, action: Any, reward: float, done: bool, error: Optional[str]) -> None:
    error_val = error if error else "null"
    done_val = str(done).lower()
    print(
        f"[STEP] step={step} action={action} reward={reward:.2f} done={done_val} error={error_val}",
        flush=True,
    )

def log_end(success: bool, steps: int, rewards: List[float]) -> None:
    rewards_str = ",".join(f"{r:.2f}" for r in rewards)
    # Corrected format: Removed 'score' to match exact guideline specimen
    print(f"[END] success={str(success).lower()} steps={steps} rewards={rewards_str}", flush=True)

async def main() -> None:
    env = HallucinationEnv()
    all_task_rewards = []
    
    # Evaluate baseline tasks
    for i in range(3):
        task_name = f"hallucination_task_{i+1}"
        rewards: List[float] = []
        steps_taken = 0
        success = False
        score = 0.0
        
        log_start(task=task_name, env=BENCHMARK, model=MODEL_NAME)
        
        try:
            obs = await env.reset()
            done = False
            
            for step in range(1, MAX_STEPS + 1):
                try:
                    response = client.chat.completions.create(
                        model=MODEL_NAME,
                        messages=[
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
                        temperature=0
                    )
                    
                    content = response.choices[0].message.content
                    action_data = json.loads(content)
                    action = Action(**action_data)
                    action_str = str(action.is_hallucination)
                except Exception as e:
                    logger.error(f"Inference error: {e}")
                    # Safe fallback with mandatory fields
                    action = Action(
                        is_hallucination=False, 
                        confidence=0.0, 
                        risk_level="Low", 
                        recommended_action="Review",
                        reasoning=f"Error: {e}"
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
            log_end(success=success, steps=steps_taken, rewards=rewards)

    avg_score = sum(all_task_rewards) / len(all_task_rewards) if all_task_rewards else 0.0
    print(f"\nFINAL REPRODUCIBLE BASELINE SCORE: {avg_score:.2f}")

if __name__ == "__main__":
    asyncio.run(main())
