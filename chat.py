import random
import json
import torch
from model import NeuralNet
from nltk_utils import bag_of_words, tokenize

device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

# Load intents
with open("data.json", 'r', encoding='utf-8') as json_data:
    intents = json.load(json_data)

# Load trained model
FILE = "model.pth"
data = torch.load(FILE)

input_size = data["input_size"]
hidden_size = data["hidden_size"]
output_size = data["output_size"]
all_words = data["all_words"]
tags = data["tags"]
model_state = data["model_state"]

# Reconstruct model
model = NeuralNet(input_size, hidden_size, output_size).to(device)
model.load_state_dict(model_state)
model.eval()

# Context memory
bot_name = "CineMate"
last_tag = None
rejection_count = 0
ask_to_switch = False

rejection_keywords = ["another","i've seen it", "seen it", "don't like it", "something else", "another one", "not good", "don't want that","i dont like"]
surprise_keywords = ["surprise me", "anything", "whatever", "you choose", "i don't know"]
actor_movies = {
    "leonardo dicaprio": ["Inception", "The Revenant", "The Wolf of Wall Street", "Titanic"],
    "emma stone": ["La La Land", "Easy A", "Cruella"],
    "keanu reeves": ["John Wick", "The Matrix", "Speed"],
    "ryan gosling": ["Drive", "The Notebook", "Blade Runner 2049"],
    "natalie portman": ["Black Swan", "V for Vendetta", "Thor"],
    "dwayne johnson": ["Jumanji", "San Andreas", "Rampage"],
    "the rock": ["Jumanji", "Hobbs & Shaw", "Skyscraper"],  # alias for Dwayne Johnson
    "tom cruise": ["Top Gun: Maverick", "Mission: Impossible", "Edge of Tomorrow"],
    "brad pitt": ["Fight Club", "Troy", "Once Upon a Time in Hollywood"],
    "robert de niro": ["Taxi Driver", "The Irishman", "Raging Bull"],
    "al pacino": ["Scarface", "The Godfather", "Scent of a Woman"],
    "meryl streep": ["The Devil Wears Prada", "Sophie's Choice", "Mamma Mia!"]
}

print("Let's chat! (type 'quit' to stop)")
def get_bot_response(sentence):
    global last_tag, rejection_count, ask_to_switch

    # Handle rejections
    if any(kw in sentence.lower() for kw in rejection_keywords):
        if last_tag:
            rejection_count += 1
            if rejection_count >= 3:
                ask_to_switch = True
                return "You didn’t like any of those. Would you like to switch genres?"
            else:
                for intent in intents["intents"]:
                    if intent["tag"] == last_tag:
                        return f"Okay, how about this one: {random.choice(intent['responses'])}"
        else:
            return "I’m not sure which genre you want. Could you tell me again?"

    # Handle response to "switch genres?"
    if ask_to_switch:
        if "yes" in sentence.lower():
            last_tag = None
            rejection_count = 0
            ask_to_switch = False
            return "Alright, what other genre are you in the mood for?"
        elif "no" in sentence.lower():
            rejection_count = 0
            ask_to_switch = False
            for intent in intents["intents"]:
                if intent["tag"] == last_tag:
                    return f"Okay, sticking with {last_tag}. What about this: {random.choice(intent['responses'])}"

    # Surprise mode
    if any(kw in sentence.lower() for kw in surprise_keywords):
        random_intent = random.choice(intents["intents"])
        last_tag = random_intent["tag"]
        return f"Surprise! How about this: {random.choice(random_intent['responses'])}"

    # Actor-based recommendation
    matched_actor = None
    for actor in actor_movies:
        if actor in sentence.lower():
            matched_actor = actor
            break
    if matched_actor:
        recommendation = random.choice(actor_movies[matched_actor])
        last_tag = "actor_movie"
        rejection_count = 0
        ask_to_switch = False
        return f"How about *{recommendation}* with {matched_actor.title()}?"

    # Use NLP model
    sentence_tokens = tokenize(sentence)
    X = bag_of_words(sentence_tokens, all_words)
    X = torch.tensor(X, dtype=torch.float32).to(device)
    X = X.unsqueeze(0)

    output = model(X)
    _, predicted = torch.max(output, dim=1)
    tag = tags[predicted.item()]
    probs = torch.softmax(output, dim=1)
    prob = probs[0][predicted.item()]

    if prob.item() > 0.75:
        for intent in intents["intents"]:
            if tag == intent["tag"]:
                if tag not in ["greeting", "thanks", "goodbye"]:
                    last_tag = tag
                rejection_count = 0
                ask_to_switch = False
                return random.choice(intent["responses"])
    else:
        last_tag = None  # forget the last tag if confusion happens
        return "Hmm... I’m not sure I understand. Can you rephrase?"
