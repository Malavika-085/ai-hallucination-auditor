import json
from typing import Any, Dict, Optional, Tuple
from openenv_core import Environment
from models import Action, Observation, Reward
from tasks import TASKS, grade_action

class HallucinationEnv(Environment):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.current_task_idx = -1
        self.total_reward = 0.0
        self.done = False

    async def reset(self, options: Optional[Dict[str, Any]] = None) -> Observation:
        """
        Resets the environment and loads the next task (Async).
        """
        self.current_task_idx = (self.current_task_idx + 1) % len(TASKS)
        task = TASKS[self.current_task_idx]
        
        self.done = False
        return Observation(
            question=task["question"],
            model_answer=task["model_answer"]
        )

    async def step(self, action: Action) -> Tuple[Observation, float, bool, Dict[str, Any]]:
        """
        Evaluates the auditor's classification (Async).
        """
        if self.done:
            raise RuntimeError("Step called on terminated environment. Please call reset().")
            
        task = TASKS[self.current_task_idx]
        reward_score = grade_action(action, task)
        
        self.total_reward += reward_score
        self.done = True 
        
        obs = Observation(question=task["question"], model_answer=task["model_answer"])
        info = {
            "task_difficulty": task["difficulty"],
            "ground_truth": task["is_hallucination"],
            "reward_breakdown": f"Score: {reward_score:.2f}"
        }
        
        return obs, reward_score, self.done, info

    async def close(self):
        """Cleanup environment."""
        pass

    def state(self) -> Dict[str, Any]:
        task = TASKS[self.current_task_idx] if self.current_task_idx >= 0 else None
        return {
            "current_task_idx": self.current_task_idx,
            "current_task_name": task["difficulty"] if task else "None",
            "total_reward": round(self.total_reward, 2),
            "tasks_completed": self.current_task_idx + 1 if self.current_task_idx >= 0 else 0,
            "is_done": self.done
        }
