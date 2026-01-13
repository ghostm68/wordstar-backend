from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import pennylane as qml
import numpy as np

app = FastAPI()

# Allow your Cloudflare site to talk to this Brain
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # We can lock this down to 'wordstar.nexus' later
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- QUANTUM LOGIC ---
dev = qml.device("default.qubit", wires=2)

@qml.qnode(dev)
def get_quantum_random_number():
    # True Randomness via Superposition
    qml.Hadamard(wires=0)
    qml.Hadamard(wires=1)
    return qml.probs(wires=[0, 1])

# --- VOCABULARY ---
nouns = ["nebula", "echo", "whisper", "chronometer", "void", "nexus", "fragment", "signal", "horizon"]
verbs = ["fractured", "hummed", "collapsed", "drifted", "ignited", "observed", "shattered", "pulsed"]
adjectives = ["silent", "obsidian", "infinite", "hollow", "electric", "forgotten", "crimson", "static"]

@app.get("/generate")
def generate_muse():
    # 1. Run Quantum Circuit
    probs = get_quantum_random_number()
    
    # 2. Pick words based on quantum probability
    # We flatten probs to a standard list for numpy
    flat_probs = np.array(probs).flatten()
    
    # Generate 3 sentences
    sentences = []
    for _ in range(3):
        n = np.random.choice(nouns, p=flat_probs)
        v = np.random.choice(verbs, p=flat_probs)
        a = np.random.choice(adjectives, p=flat_probs)
        sentences.append(f"The {a} {n} {v}.")
        
    paragraph = " ".join(sentences)
    
    return {
        "status": "Quantum State Collapsed",
        "muse": paragraph
    }
