import sys

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except Exception:
        pass

import json
import os
from rich.console import Console

console = Console()

# File paths
EMBEDDINGS_FILE = "embeddings.json"
MAPPING_FILE = "names.json"

def load_embeddings():
    """Load the precomputed vector embeddings for known persons."""
    if not os.path.exists(EMBEDDINGS_FILE):
        console.print("[bold red]⚠️ Embeddings file not found! Run setup.py first.[/bold red]")
        return None
    try:
        with open(EMBEDDINGS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        console.print(f"[bold red]⚠️ Error reading {EMBEDDINGS_FILE}: {e}[/bold red]")
        return None

def load_person_mapping():
    """
    Load optional filename-to-nickname / display name mapping.
    Expected format in names.json:
      {"image_filename_without_ext": "Display Name / Nickname"}
    or:
      [{"id": "image_filename_without_ext", "name": "Display Name / Nickname"}]
    """
    if not os.path.exists(MAPPING_FILE):
        return {}
    try:
        with open(MAPPING_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            if isinstance(data, dict):
                return data
            elif isinstance(data, list):
                mapping = {}
                for item in data:
                    if isinstance(item, dict):
                        key = item.get("id") or item.get("filename")
                        val = item.get("name") or item.get("nickname")
                        if key and val:
                            mapping[key] = val
                return mapping
    except Exception as e:
        console.print(f"[bold yellow]⚠️ Could not load {MAPPING_FILE}: {e}[/bold yellow]")
    return {}

def identify_face(test_image_path, threshold=0.45):
    """
    Identify a face in the test image by computing its embedding using ArcFace and comparing
    it with stored embeddings using cosine similarity.
    
    :param test_image_path: Path to the test image.
    :param threshold: Minimum cosine similarity required to consider a match (default: 0.45).
    """
    embeddings = load_embeddings()
    if embeddings is None:
        return {"success": False, "error": "Embeddings file not found. Please run setup.py first."}

    if not embeddings:
        return {"success": False, "error": "No person embeddings found. Place images in 'faces/' and run setup.py."}

    person_mapping = load_person_mapping()

    test_image_path = os.path.abspath(test_image_path)
    if not os.path.exists(test_image_path):
        console.print("[bold red]⚠️ Test image not found![/bold red]")
        return {"success": False, "error": "Test image not found"}

    try:
        from deepface import DeepFace
        import numpy as np
    except ImportError as e:
        console.print(f"[bold red]❌ Machine learning dependencies missing: {e}[/bold red]")
        return {"success": False, "error": f"Machine learning dependency missing ({e}). Run 'pip install -r requirements.txt' or test using 'python app_test.py'."}

    try:
        # Generate embedding for the test image using ArcFace and retinaface
        representations = DeepFace.represent(
            test_image_path,
            model_name="ArcFace",
            detector_backend="retinaface",
            enforce_detection=False
        )

        if not representations:
            console.print("[bold red]❌ No face detected in the test image.[/bold red]")
            return {"success": False, "error": "No face detected"}

        # Normalize test embedding
        test_embedding = np.array(representations[0]["embedding"])
        test_embedding = test_embedding / np.linalg.norm(test_embedding)

        best_match_id = None
        best_similarity = -1.0  # Cosine similarity ranges from -1 to 1

        # Compare the test embedding with stored person embeddings using cosine similarity.
        # Since both vectors are L2-normalized, the dot product equals cosine similarity.
        for person_id, stored_embedding in embeddings.items():
            stored_vec = np.array(stored_embedding)
            similarity = float(np.dot(test_embedding, stored_vec))

            if similarity > best_similarity:
                best_similarity = similarity
                best_match_id = person_id

        confidence = best_similarity * 100.0  # Expressed as a percentage
        # Default display name is the image filename itself unless an optional nickname mapping exists
        best_match_name = person_mapping.get(best_match_id, best_match_id)

        # Check if similarity exceeds threshold
        match_found = best_similarity >= threshold
        
        result = {
            "success": True,
            "match_found": bool(match_found),
            "id": best_match_id,
            "name": best_match_name,
            "confidence": float(confidence),
            "similarity": float(best_similarity)
        }

        display_label = f"{best_match_name} ({best_match_id})" if best_match_name != best_match_id else best_match_name

        if match_found:
            console.print(
                f"[bold green]✅ Match found:[/bold green] [bold cyan]{display_label}[/bold cyan] with [bold yellow]{confidence:.2f}%[/bold yellow] confidence."
            )
        else:
            console.print(
                f"[bold red]❌ No exact match found.[/bold red] Closest match: [bold cyan]{display_label}[/bold cyan] with [bold yellow]{confidence:.2f}%[/bold yellow] confidence."
            )
            
        return result

    except Exception as e:
        console.print(f"[bold red]❌ Error processing test image: {e}[/bold red]")
        return {"success": False, "error": str(e)}

if __name__ == "__main__":
    import sys
    test_path = sys.argv[1] if len(sys.argv) > 1 else os.path.join("test", "sample.png")
    identify_face(test_path)
