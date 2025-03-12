import faiss
import numpy as np
import os
from sentence_transformers import SentenceTransformer

# Define FAISS index
VECTOR_DIMENSION = 384  # MiniLM-L6-v2 has 384 dimensions
index = faiss.IndexFlatL2(VECTOR_DIMENSION)

# Store file metadata (mapping file IDs to paths)
file_metadata = {}

# Load AI model to generate text embeddings
embedding_model = SentenceTransformer('all-MiniLM-L6-v2')

def file_to_vector(file_path):
    """Convert a file's contents into a vector embedding."""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
        return embedding_model.encode(content)  # Convert text to vector
    except Exception as e:
        print(f"[VECTOR ERROR] Could not process {file_path}: {e}")
        return None

def add_file_to_index(file_path):
    """Adds or updates a file in the FAISS vector store."""
    vector = file_to_vector(file_path)
    if vector is not None:
        file_id = len(file_metadata)  # Assign a unique ID
        index.add(np.array([vector]))  # Add vector to FAISS
        file_metadata[file_id] = file_path  # Store file metadata
        print(f"[VECTOR STORE] Indexed file: {file_path}")

def remove_file_from_index(file_path):
    """Removes a file from the FAISS vector store when deleted."""
    for file_id, path in list(file_metadata.items()):
        if path == file_path:
            index.remove_ids(np.array([file_id]))  # Remove vector
            del file_metadata[file_id]
            print(f"[VECTOR STORE] Removed file: {file_path}")
            return
    print(f"[VECTOR STORE] File not found: {file_path}")

def search_file(query):
    """Search FAISS for the most relevant file based on a query."""
    query_vector = embedding_model.encode(query)  # Convert query to vector
    _, nearest_ids = index.search(np.array([query_vector]), k=1)  # Find closest match
    nearest_file = file_metadata.get(nearest_ids[0][0], "No matching file found")
    return nearest_file

# Auto-update FAISS when files change
def save_to_project(file_path, content):
    """Save file and update FAISS index."""
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"[+] AI created/modified file: {file_path}")
    add_file_to_index(file_path)

def delete_file(file_path):
    """Delete file and remove it from FAISS."""
    if os.path.exists(file_path):
        os.remove(file_path)
        remove_file_from_index(file_path)
        print(f"[-] AI deleted file: {file_path}")
