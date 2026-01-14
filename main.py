from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import pennylane as qml
import numpy as np
import requests
import re
from collections import Counter

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

# --- QUANTUM LOGIC ---
dev = qml.device("default.qubit", wires=5)

@qml.qnode(dev, interface='numpy')
def get_quantum_random_number():
    # Put all 5 qubits in superposition
    for i in range(5):
        qml.Hadamard(wires=i)
    return qml.probs(wires=[0, 1, 2, 3, 4])

# --- THE LEDGER INGESTER (NEW) ---
def get_ledger_vocab():
    url = "https://raw.githubusercontent.com/ghostm68/inktwo/main/brim.txt"
    try:
        resp = requests.get(url)
        resp.raise_for_status()
        text = resp.text.lower()
        
        # Cleanup: Remove non-alphabetic chars
        clean_text = re.sub(r'[^\w\s]', '', text)
        
        # Extract words (6+ letters for deeper 'thematic' weight)
        all_words = re.findall(r'\b\w{6,}\b', clean_text)
        
        # Audit the frequency and get top 32
        counts = Counter(all_words)
        top_32_tuples = counts.most_common(32)
        
        # Extract just the words from the (word, count) tuples
        words = [t[0] for t in top_32_tuples]
        
        # If we don't have enough words, pad it with your original nouns
        if len(words) < 32:
            padding = ["nebula", "echo", "whisper", "void", "nexus", "signal"]
            words.extend(padding)
            words = words[:32] # Ensure exactly 32
            
        return words
    except Exception as e:
        print(f"Ledger Fetch Error: {e}")
        return None

# --- BACKUP VOCABULARY ---
# (Used for verbs/adjectives or if the GitHub fetch fails)
nouns_backup = ["nebula", "echo", "whisper", "chronometer", "void", "nexus", "fragment", "signal", "horizon", "monolith", "algorithm", "spectre", "isotope", "vortex", "cipher", "drone", "glitch", "network", "phantom", "mainframe", "reactor", "synapse", "artifact", "shard", "memory", "paradox", "entropy", "vector", "protocol", "silence", "shadow", "circuit"]
verbs = ["fractured", "hummed", "collapsed", "drifted", "ignited", "observed", "shattered", "pulsed", "dissolved", "encoded", "transmitted", "erased", "aligned", "resonated", "orbited", "scanned", "corrupted", "merged", "decoded", "manifested", "echoed", "vibrated", "locked", "severed", "mapped", "synced", "traced", "hunted", "breached", "calibrated", "awoke", "slept"]
adjectives = ["silent", "obsidian", "infinite", "hollow", "electric", "forgotten", "crimson", "static", "digital", "frozen", "luminous", "fractal", "haunted", "cybernetic", "terminal", "kinetic", "dormant", "volatile", "synthetic", "solar", "magnetic", "spectral", "unseen", "ancient", "liquid", "binary", "nuclear", "astral", "chrome", "velvet", "fading", "hidden"]

@app.get("/")
def read_root():
    return {"status": "Online", "msg": "Send requests to /generate"}

@app.get("/generate")
def generate_muse():
    try:
        # 1. Fetch live nouns from brim.txt
        live_nouns = get_ledger_vocab()
        # Use backup if live fetch fails
        current_nouns = live_nouns if live_nouns else nouns_backup

        # 2. Run Quantum Circuit (Returns 32 probabilities)
        raw_probs = get_quantum_random_number()
        
        # 3. Sanitize Data
        probs = [float(p) for p in raw_probs]
        probs = np.array(probs)
        probs /= probs.sum() # Ensure they equal exactly 1.0
        
        # 4. Generate sentences
        sentences = []
        for _ in range(3):
            # Select words based on Quantum State
            n = np.random.choice(current_nouns, p=probs)
            v = np.random.choice(verbs, p=probs)
            a = np.random.choice(adjectives, p=probs)
            sentences.append(f"The {a} {n} {v}.")
            
        paragraph = " ".join(sentences)
        
        return {
            "status": "Quantum State Collapsed (Entangled with brim.txt)",
            "muse": paragraph,
            "source": "GitHub/brim.txt" if live_nouns else "Backup List"
        }
        
    except Exception as e:
        return {
            "status": "ERROR",
            "muse": f"System Failure: {str(e)}"
        }
