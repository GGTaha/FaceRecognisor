import sys

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except Exception:
        pass

import argparse
import json
import os
import numpy as np
from deepface import DeepFace

# Default directory containing person reference images
DEFAULT_FACES_DIR = "faces"
EMBEDDINGS_FILE = "embeddings.json"

def get_image_files(directory):
    """Retrieve all image file paths from the given directory."""
    image_files = []
    valid_extensions = {".jpg", ".png", ".jpeg", ".webp", ".bmp"}
    
    for file in os.listdir(directory):
        if os.path.splitext(file)[1].lower() in valid_extensions:
            image_files.append(os.path.join(directory, file))
    
    return image_files

def generate_embeddings(faces_dir=DEFAULT_FACES_DIR):
    """
    Generate face embeddings for all images in the faces directory.
    Uses the file name (without extension) as the person identifier.
    """
    embeddings = {}
    
    # Check fallback directory if default does not exist
    if not os.path.exists(faces_dir):
        if os.path.exists("known_faces"):
            faces_dir = "known_faces"
        else:
            os.makedirs(faces_dir, exist_ok=True)
            print(f"📁 Created folder '{faces_dir}'. Please place person photos here (e.g., 'john_doe.jpg') and rerun setup.")
            return

    image_files = get_image_files(faces_dir)
    if not image_files:
        print(f"⚠️ No images found in '{faces_dir}'. Place person photos in this folder and rerun setup.")
        return

    print(f"🔍 Found {len(image_files)} image(s) in '{faces_dir}'. Generating embeddings...")

    for img_path in image_files:
        # Use filename (without extension) as the identifying person name/ID
        person_name = os.path.splitext(os.path.basename(img_path))[0]
        
        try:
            # Generate face embedding using ArcFace with RetinaFace detection
            representations = DeepFace.represent(
                img_path,
                model_name="ArcFace",
                detector_backend="retinaface",
                enforce_detection=False
            )
            
            if not representations:
                print(f"❌ No face detected in {img_path}, skipping.")
                continue
            
            # Normalize embedding vector
            embedding = np.array(representations[0]["embedding"])
            embedding = embedding / np.linalg.norm(embedding)
            
            # Store embedding keyed by the person's name (filename)
            embeddings[person_name] = embedding.tolist()
            print(f"✅ Processed Person: {person_name}")
        
        except Exception as e:
            print(f"❌ Error processing {img_path}: {e}")

    # Save embeddings to file
    with open(EMBEDDINGS_FILE, "w", encoding="utf-8") as f:
        json.dump(embeddings, f, indent=4, ensure_ascii=False)
    
    print(f"\n💾 Saved {len(embeddings)} person embeddings to '{EMBEDDINGS_FILE}'")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate facial embeddings for known persons.")
    parser.add_argument("--faces-dir", default=DEFAULT_FACES_DIR, help="Path to reference face images directory (default: 'faces')")
    args = parser.parse_args()

    generate_embeddings(args.faces_dir)
