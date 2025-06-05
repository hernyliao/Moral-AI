import re
import spacy
import random
import json

WEB_JSON_PATH = "web.json"

def load_correlation_web():
    with open(WEB_JSON_PATH, "r") as file:
        data = json.load(file)
        web = {}
        for action, entities in data.items():
            for entity, score in entities.items():
                web[(action, entity)] = score
        return web

def save_correlation_web(web):
    data = {}
    for (action, entity), score in web.items():
        if action not in data:
            data[action] = {}
        data[action][entity] = score
    with open(WEB_JSON_PATH, "w") as f:
        json.dump(data, f, indent=2)

def parse_question(question):
    parser = spacy.load("en_core_web_sm")
    question = parser(question.lower().strip().rstrip("?.!"))

    for word in question:
        if word.pos_ == "VERB" and not action:
            action = word.lemma_
        if word.pos_ in {"NOUN", "PROPN"} and not entity:
            entity = word.lemma_
    return action, entity

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
    elif score == 0: # so that learning process can steer in the right direction
        random_choice = random.choice([1, -1]) 
        if random_choice == 1:
            judgement = "good"
        else:
            judgement = "bad"
    
    return score, judgement

def update_correlation_web(action, entity, mod, web):
    key = (action, entity)
    web[key] = web.get(key, 0) + mod
    save_correlation_web(web)

def answer_moral_question(question):
    web = load_correlation_web()
    action, entity = parse_question(question)

    if not action or not entity:
        return "Sorry, I couldn't understand the question."
    
    score, judgement = evaluate_moral_judgement(action, entity, web)
    explanation = explanation = f"The action '{action}' on '{entity}' has a moral score of {score}."
    print(f"Judgement: {judgement}. {explanation}")

    feedback = input("Was this correct? (yes/no): ").strip().lower()
    if feedback in {"yes", "no"}:
        if (feedback == "yes" and judgement == "good") or (feedback == "no" and judgement == "bad"):
            mod = 1
        else:
            mod = -1
        update_correlation_web(action, entity, mod, web)
        return "Moral score updated."

while True:
    question = input('Ask a moral question ([ing-verb] + [entity]) ("exit" to quit): ')
    if question.strip().lower() in {"exit", "quit"}:
        print("Goodbye!")
        break
    print(answer_moral_question(question))