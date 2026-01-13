from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import pennylane as qml
import numpy as np

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- QUANTUM LOGIC ---
# UPGRADE: We are now using 3 Qubits to get 8 outcomes (2^3 = 8)
dev = qml.device("default.qubit", wires=3)

@qml.qnode(dev, interface='numpy')
def get_quantum_random_number():
    # Put all 3 qubits in superposition
    qml.Hadamard(wires=0)
    qml.Hadamard(wires=1)
    qml.Hadamard(wires=2)
    # This returns exactly 8 probability values
    return qml.probs(wires=[0, 1, 2])

# --- VOCABULARY ---
# CRITICAL FIX: All lists must have exactly 8 items to match the 8 quantum states
nouns =      ["nebula", "echo", "whisper", "chronometer", "void", "nexus", "fragment", "signal"]
verbs =      ["fractured", "hummed", "collapsed", "drifted", "ignited", "observed", "shattered", "pulsed"]
adjectives = ["silent", "obsidian", "infinite", "hollow", "electric", "forgotten", "crimson", "static"]

@app.get("/")
def read_root():
    return {"status": "Online", "msg": "Send requests to /generate"}

@app.get("/generate")
def generate_muse():
    try:
        # 1. Run Quantum Circuit
        raw_probs = get_quantum_random_number()
        
        # 2. Sanitize Data
        probs = [float(p) for p in raw_probs]
        probs = np.array(probs)
        probs /= probs.sum() # Ensure they equal 1.0
        
        # 3. Generate sentences
        sentences = []
        for _ in range(3):
            # Now 'nouns' has 8 items and 'probs' has 8 items. Perfect match.
            n = np.random.choice(nouns, p=probs)
            v = np.random.choice(verbs, p=probs)
            a = np.random.choice(adjectives, p=probs)
            sentences.append(f"The {a} {n} {v}.")
            
        paragraph = " ".join(sentences)
        
        return {
            "status": "Quantum State Collapsed",
            "muse": paragraph
        }
        
    except Exception as e:
        return {
            "status": "ERROR",
            "muse": f"System Failure: {str(e)}"
        }
