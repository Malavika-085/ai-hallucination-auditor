import os
import json
import logging
import requests
from typing import List, Dict, Any
from pydantic import ValidationError
from env import HallucinationEnv
from models import Action

# Configure Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("AuditorInference")

# Environment Constraints (Required by Hackathon Validator)
API_BASE_URL = os.environ["API_BASE_URL"]
API_KEY = os.environ["API_KEY"]
MODEL_NAME = os.environ.get("MODEL_NAME", "gpt-4o")

def run_auditor():
    env = HallucinationEnv()
    
    all_task_rewards = []
    
    # Evaluate 3 tasks: Easy, Medium, Hard
    for task_idx in range(3):
        obs = env.reset()
        task_name = f"Task_{task_idx + 1}"
        
        print(f"\n[START] task={task_name} env=hallucination_auditor model={MODEL_NAME}")
        
        task_rewards = []
        done = False
        step_count = 0
        max_steps = 3
        
        while not done and step_count < max_steps:
            step_count += 1
            
            # Direct HTTP call to ensure proxy detection
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
                response.raise_for_status()
                
                result = response.json()
                content = result["choices"][0]["message"]["content"]
                action_data = json.loads(content)
                action = Action(**action_data)
                
                obs, reward, done, info = env.step(action)
                task_rewards.append(reward)
                
                print(f"[STEP] step={step_count} action={action.is_hallucination} risk={action.risk_level} reward={reward:.2f} done={done} error=none")
                
            except Exception as e:
                print(f"[STEP] step={step_count} action=N/A reward=0.0 done=True error={str(e)}")
                task_rewards.append(0.0)
                done = True
                
        # End Task Reporting
        all_task_rewards.append(sum(task_rewards))
        success = sum(task_rewards) > 0.6
        final_task_score = sum(task_rewards) / len(task_rewards) if task_rewards else 0.0
        
        print(f"[END] success={success} steps={step_count} score={final_task_score:.2f} rewards={task_rewards}")

    # Final Normalized Baseline Score (Reproducible)
    avg_total_reward = sum(all_task_rewards) / 3
    print(f"\nFINAL REPRODUCIBLE BASELINE SCORE: {avg_total_reward:.2f}")

if __name__ == "__main__":
    run_auditor()
