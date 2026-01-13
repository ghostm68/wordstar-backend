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
# We use interface='numpy' to ensure compatibility
dev = qml.device("default.qubit", wires=2)

@qml.qnode(dev, interface='numpy')
def get_quantum_random_number():
    qml.Hadamard(wires=0)
    qml.Hadamard(wires=1)
    return qml.probs(wires=[0, 1])

# --- VOCABULARY ---
nouns = ["nebula", "echo", "whisper", "chronometer", "void", "nexus", "fragment", "signal", "horizon"]
verbs = ["fractured", "hummed", "collapsed", "drifted", "ignited", "observed", "shattered", "pulsed"]
adjectives = ["silent", "obsidian", "infinite", "hollow", "electric", "forgotten", "crimson", "static"]

@app.get("/")
def read_root():
    return {"status": "Online", "msg": "Send requests to /generate"}

@app.get("/generate")
def generate_muse():
    try:
        # 1. Run Quantum Circuit
        raw_probs = get_quantum_random_number()
        
        # 2. SANITIZE THE DATA (The Fix)
        # Convert to standard python list of floats to avoid TypeErrors
        probs = [float(p) for p in raw_probs]
        
        # Ensure they sum to EXACTLY 1.0 to prevent numpy crashes
        probs = np.array(probs)
        probs /= probs.sum() 
        
        # 3. Generate sentences
        sentences = []
        for _ in range(3):
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
        # This prints the error to the browser instead of crashing
        return {
            "status": "ERROR",
            "muse": f"System Failure: {str(e)}"
        }
