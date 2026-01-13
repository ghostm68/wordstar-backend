from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import pennylane as qml
import numpy as np

app = FastAPI()

# SECURITY LOCK
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://wordstar.nexus", 
        "https://muse.wordstar.nexus",
        "http://localhost:8080"
    ],
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- QUANTUM LOGIC (UPGRADE) ---
# We are upgrading to 5 Qubits (2^5 = 32 outcomes)
# We stick to default.qubit because it is safer for Render's free tier than Lightning
dev = qml.device("default.qubit", wires=5)

@qml.qnode(dev, interface='numpy')
def get_quantum_random_number():
    # Put all 5 qubits in superposition
    for i in range(5):
        qml.Hadamard(wires=i)
    
    # Return 32 probabilities
    return qml.probs(wires=[0, 1, 2, 3, 4])

# --- VOCABULARY (32 Words per Category) ---
nouns = [
    "nebula", "echo", "whisper", "chronometer", "void", "nexus", "fragment", "signal",
    "horizon", "monolith", "algorithm", "spectre", "isotope", "vortex", "cipher", "drone",
    "glitch", "network", "phantom", "mainframe", "reactor", "synapse", "artifact", "shard",
    "memory", "paradox", "entropy", "vector", "protocol", "silence", "shadow", "circuit"
]

verbs = [
    "fractured", "hummed", "collapsed", "drifted", "ignited", "observed", "shattered", "pulsed",
    "dissolved", "encoded", "transmitted", "erased", "aligned", "resonated", "orbited", "scanned",
    "corrupted", "merged", "decoded", "manifested", "echoed", "vibrated", "locked", "severed",
    "mapped", "synced", "traced", "hunted", "breached", "calibrated", "awoke", "slept"
]

adjectives = [
    "silent", "obsidian", "infinite", "hollow", "electric", "forgotten", "crimson", "static",
    "digital", "frozen", "luminous", "fractal", "haunted", "cybernetic", "terminal", "kinetic",
    "dormant", "volatile", "synthetic", "solar", "magnetic", "spectral", "unseen", "ancient",
    "liquid", "binary", "nuclear", "astral", "chrome", "velvet", "fading", "hidden"
]

@app.get("/")
def read_root():
    return {"status": "Online", "msg": "Send requests to /generate"}

@app.get("/generate")
def generate_muse():
    try:
        # 1. Run Quantum Circuit (Returns 32 probs)
        raw_probs = get_quantum_random_number()
        
        # 2. Sanitize Data
        probs = [float(p) for p in raw_probs]
        probs = np.array(probs)
        probs /= probs.sum() # Ensure they equal exactly 1.0
        
        # 3. Generate sentences
        sentences = []
        for _ in range(3):
            # Numpy will now pick from 32 words using 32 probabilities
            n = np.random.choice(nouns, p=probs)
            v = np.random.choice(verbs, p=probs)
            a = np.random.choice(adjectives, p=probs)
            sentences.append(f"The {a} {n} {v}.")
            
        paragraph = " ".join(sentences)
        
        return {
            "status": "Quantum State Collapsed (5 Qubits)",
            "muse": paragraph
        }
        
    except Exception as e:
        return {
            "status": "ERROR",
            "muse": f"System Failure: {str(e)}"
        }
