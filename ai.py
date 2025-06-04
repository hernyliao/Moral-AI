"""
Outline for AI Moral Reasoning System

1. Define Data Structures
    - Word associations (connotations)
    - Entities (e.g., baby, mosquito)
    - Actions (e.g., killing)
    - Moral weights

2. Load or Initialize Knowledge Base
    - Predefined associations between actions and entities
    - Mechanism to update or expand associations

3. Input Processing
    - Parse moral question (e.g., "Is killing a baby bad?")
    - Identify action and entity from input

4. Moral Evaluation Logic
    - Retrieve association score between action and entity
    - Apply reasoning rules to determine moral judgment

5. Output Generation
    - Generate answer based on evaluation
    - Optionally, provide explanation for the answer

6. (Optional) Learning/Feedback Mechanism
    - Update associations based on user feedback or new data

# Next steps: Implement each section as functions/classes.
"""

import re
import random
import json
import os

WEB_JSON_PATH = "web.json"

def load_knowledge_base():
    if not os.path.exists(WEB_JSON_PATH) or os.stat(WEB_JSON_PATH).st_size == 0:
        # Initialize with default knowledge base if file doesn't exist or is empty
        kb = {
            ('killing', 'baby'): -10,
            ('killing', 'mosquito'): 10,
            ('helping', 'elderly'): 8,
            ('stealing', 'money'): -7,
        }
        save_knowledge_base(kb)
        return kb
    with open(WEB_JSON_PATH, "r") as f:
        data = json.load(f)
        # Convert keys back to tuples
        return {tuple(k.split('|')): v for k, v in data.items()}

def save_knowledge_base(kb):
    # Convert tuple keys to strings for JSON
    data = {'|'.join(k): v for k, v in kb.items()}
    with open(WEB_JSON_PATH, "w") as f:
        json.dump(data, f, indent=2)

def parse_question(question):
    """Parse a moral question and return the action and entity involved."""
    q = question.lower().strip().rstrip("?.!")
    # Remove trailing conditional clauses starting with common keywords
    q = re.split(r"\bif\b|\bbecause\b|\bwhen\b|\bwhile\b", q)[0]
    match = re.search(r"(killing|helping|stealing)\s+(?:a|an|the)?\s*(\w+)", q)
    if not match:
        match = re.search(r"(\w+)\s+(?:a|an|the)?\s*(\w+)", q)
    if match:
        action, entity = match.group(1), match.group(2)
        return action, entity
    return None, None

def evaluate_moral_judgement(action, entity, kb):
    key = (action, entity)
    if key not in kb:
        kb[key] = 0  # Add unfamiliar pair with score 0
        save_knowledge_base(kb)
    score = kb.get(key, 0)
    if score > 0:
        judgement = "good"
    elif score < 0:
        judgement = "bad"
    elif score == 0:
        random_choice = random.choice([1, -1])
        judgement = "good" if random_choice == 1 else "bad"
    explanation = f"The action '{action}' on '{entity}' has a moral score of {score}."
    return score, judgement, explanation

def update_knowledge_base(action, entity, delta, kb):
    key = (action, entity)
    kb[key] = kb.get(key, 0) + delta
    save_knowledge_base(kb)

def answer_moral_question(question):
    kb = load_knowledge_base()
    action, entity = parse_question(question)
    if not action or not entity:
        return "Sorry, I couldn't understand the question."
    score, judgement, explanation = evaluate_moral_judgement(action, entity, kb)
    print(f"Judgement: {judgement}. {explanation}")
    feedback = input("Was this correct? (yes/no): ").strip().lower()
    if feedback in {"yes", "no"}:
        if (feedback == "yes" and judgement == "good") or (feedback == "no" and judgement == "bad"):
            delta = 1
        else:
            delta = -1
        update_knowledge_base(action, entity, delta, kb)
        return "Moral score updated."
    else:
        return "No feedback received."

# Example usage:
if __name__ == "__main__":
    question = input("Ask a moral question: ")
    print(answer_moral_question(question))
