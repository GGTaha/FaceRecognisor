from deepface import DeepFace
import json
import numpy as np
import os
from rich.console import Console

console = Console()

# Load precomputed embeddings
EMBEDDINGS_FILE = "embeddings.json"
STUDENT_DATA_FILE = "student_data_full.json"

def load_embeddings():
    if not os.path.exists(EMBEDDINGS_FILE):
        console.print("[bold red]⚠️ Embeddings file not found! Run main.py first.[/bold red]")
        return None
    with open(EMBEDDINGS_FILE, "r") as f:
        return json.load(f)

def load_student_data():
    if not os.path.exists(STUDENT_DATA_FILE):
        console.print("[bold red]⚠️ Student data file not found![/bold red]")
        return {}
    with open(STUDENT_DATA_FILE, "r") as f:
        return {student["StudentID"]: student["Name"] for student in json.load(f)}

def identify_face(test_image_path, threshold=0.45):
    """
    Identify a face in the test image by computing its embedding using ArcFace and comparing
    it with stored embeddings using cosine similarity. A higher similarity (closer to 1) indicates
    a better match.
    
    :param test_image_path: Path to the test image.
    :param threshold: Minimum cosine similarity required to consider a match (default: 0.8).
    """
    embeddings = load_embeddings()
    student_data = load_student_data()
    if embeddings is None:
        return

    test_image_path = os.path.abspath(test_image_path)
    if not os.path.exists(test_image_path):
        console.print("[bold red]⚠️ Test image not found![/bold red]")
        return

    try:
        # Generate embedding for the test image using ArcFace and retinaface for robust detection.
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
        best_similarity = -1  # Cosine similarity ranges from -1 to 1

        # Compare the test embedding with stored embeddings using cosine similarity.
        # Since both embeddings are normalized, the dot product gives the cosine similarity.
        for student_id, stored_embedding in embeddings.items():
            stored_embedding = np.array(stored_embedding)
            similarity = np.dot(test_embedding, stored_embedding)

            if similarity > best_similarity:
                best_similarity = similarity
                best_match_id = student_id

        confidence = best_similarity * 100  # Expressed as a percentage
        best_match_name = student_data.get(best_match_id, "Unknown")

        # If similarity exceeds threshold, consider it a match.
        match_found = best_similarity >= threshold
        
        result = {
            "success": True,
            "match_found": bool(match_found),
            "id": best_match_id,
            "name": best_match_name,
            "confidence": float(confidence),
            "similarity": float(best_similarity)
        }

        if match_found:
            console.print(
                f"[bold green]✅ Match found:[/bold green] [bold cyan]{best_match_name} ({best_match_id})[/bold cyan] with [bold yellow]{confidence:.2f}%[/bold yellow] confidence."
            )
        else:
            console.print(
                f"[bold red]❌ No exact match found.[/bold red] Closest match: [bold cyan]{best_match_name} ({best_match_id})[/bold cyan] with [bold yellow]{confidence:.2f}%[/bold yellow] confidence."
            )
            
        return result

    except Exception as e:
        console.print(f"[bold red]❌ Error processing test image: {e}[/bold red]")
        return {"success": False, "error": str(e)}

if __name__ == "__main__":
    # Adjust the test image path as needed.
    test_image_path = r"test\random11.png"
    identify_face(test_image_path)
