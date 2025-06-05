import re
import random
import json

WEB_JSON_PATH = "web.json"

def load_correlation_web():
    with open(WEB_JSON_PATH, "r") as file:
        data = json.load(file)
        return {tuple(k.split('|')): v for k, v in data.items()}

def save_correlation_web(web):
    data = {}
    for (action, entity), v in web.items():
        if action not in data:
            data[action] = {}
        data[action][entity] = v
    with open(WEB_JSON_PATH, "w") as f:
        json.dump(data, f, indent=2)

def parse_question(question):
    q = question.lower().strip().rstrip("?.!")
    q = re.split(r"\bif\b|\bbecause\b|\bwhen\b|\bwhile\b", q)[0]

    # Try to match common moral actions
    match = re.search(r"(killing|helping|stealing)\s+(?:a|an|the)?\s*(\w+)", q)
    if not match:
        match = re.search(r"(\w+)\s+(?:a|an|the)?\s*(\w+)", q)
    if match:
        action, entity = match.group(1), match.group(2)
        return action, entity
    return None, None

def evaluate_moral_judgement(action, entity, web):
    key = (action, entity)
    if key not in web:
        web[key] = 0  # if not in web yet
        save_correlation_web(web)

    score = web.get(key, 0)
    if score > 0:
        judgement = "good"
    elif score < 0:
        judgement = "bad"
    elif score == 0:
        random_choice = random.choice([1, -1])
        judgement = "good" if random_choice == 1 else "bad"

    explanation = f"The action '{action}' on '{entity}' has a moral score of {score}."
    return score, judgement, explanation

def update_correlation_web(action, entity, delta, web):
    key = (action, entity)
    web[key] = web.get(key, 0) + delta
    save_correlation_web(web)

def answer_moral_question(question):
    web = load_correlation_web()
    action, entity = parse_question(question)
    if not action or not entity:
        return "Sorry, I couldn't understand the question."
    score, judgement, explanation = evaluate_moral_judgement(action, entity, web)
    print(f"Judgement: {judgement}. {explanation}")
    feedback = input("Was this correct? (yes/no): ").strip().lower()
    if feedback in {"yes", "no"}:
        if (feedback == "yes" and judgement == "good") or (feedback == "no" and judgement == "bad"):
            delta = 1
        else:
            delta = -1
        update_correlation_web(action, entity, delta, web)
        return "Moral score updated."
    else:
        return "No feedback received."

if __name__ == "__main__":
    while True:
        question = input("Ask a moral question (or type 'exit' to quit): ")
        if question.strip().lower() in {"exit", "quit"}:
            print("Goodbye!")
            break
        print(answer_moral_question(question))
