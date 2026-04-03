import os
import requests
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

API_BASE_URL = os.getenv("API_BASE_URL", "http://127.0.0.1:8000")
MODEL_NAME = os.getenv("MODEL_NAME", "gpt-4o-mini")
HF_TOKEN = os.getenv("HF_TOKEN", "dummy_token")

client = OpenAI(
    base_url=API_BASE_URL,
    api_key=HF_TOKEN
)

ENV_URL = "http://127.0.0.1:8000"


def choose_best_action(state):
    if state.get("emergency_lane") is not None:
        return state["emergency_lane"]

    lanes = {
        1: state["lane_1_cars"],
        2: state["lane_2_cars"],
        3: state["lane_3_cars"]
    }
    return max(lanes, key=lanes.get)


def normalize_score(total_reward, task_id):
    if task_id == "easy":
        score = total_reward / 15
    elif task_id == "medium":
        score = total_reward / 20
    else:
        score = total_reward / 28

    return round(max(0.0, min(1.0, score)), 3)


def safe_json(response, endpoint_name):
    try:
        return response.json()
    except Exception:
        print(f"\n[ERROR] {endpoint_name} did not return valid JSON")
        print(f"Status Code: {response.status_code}")
        print("Raw Response:")
        print(response.text)
        raise


def run_task(task_id):
    print(f"[START] task={task_id}")

    reset_response = requests.post(f"{ENV_URL}/reset", params={"task_id": task_id})
    reset_data = safe_json(reset_response, "reset")
    state = reset_data["state"]

    done = False
    total_reward = 0.0
    step_num = 0
    max_demo_steps = 20  # keep inference safe

    while not done and step_num < max_demo_steps:
        action = choose_best_action(state)

        response = requests.post(f"{ENV_URL}/step", json={"action": action})
        result = safe_json(response, "step")

        reward = result["reward"]
        done = result["done"]
        state = result["state"]
        total_reward += reward
        step_num += 1

        print(
            f"[STEP] task={task_id} step={step_num} action={action} reward={reward} done={done}"
        )

    score = normalize_score(total_reward, task_id)
    print(f"[END] task={task_id} total_reward={round(total_reward, 3)} score={score}")
    return score


if __name__ == "__main__":
    scores = {}
    for task in ["easy", "medium", "hard"]:
        scores[task] = run_task(task)

    avg_score = round(sum(scores.values()) / len(scores), 3)
    print(f"\nFinal Scores: {scores}")
    print(f"Average Score: {avg_score}")