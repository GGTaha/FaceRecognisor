from deepface import DeepFace
import json
import os
import numpy as np

# Directory containing student images
IMAGE_DIR = "downloads"  # Update this if your images are stored elsewhere
EMBEDDINGS_FILE = "embeddings.json"

def get_image_files(directory):
    """Retrieve all image file paths from the given directory."""
    image_files = []
    valid_extensions = {".jpg", ".png", ".jpeg"}
    
    for file in os.listdir(directory):
        if os.path.splitext(file)[1].lower() in valid_extensions:
            image_files.append(os.path.join(directory, file))
    
    return image_files

def generate_embeddings():
    embeddings = {}
    
    # Ensure the directory exists
    if not os.path.exists(IMAGE_DIR):
        print(f"❌ Error: Directory '{IMAGE_DIR}' not found.")
        return
    
    image_files = get_image_files(IMAGE_DIR)
    if not image_files:
        print("⚠️ No images found in the directory.")
        return
    
    for img_path in image_files:
        student_id = os.path.splitext(os.path.basename(img_path))[0]  # Extract ID from filename
        
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
            
            # Normalize embedding
            embedding = np.array(representations[0]["embedding"])
            embedding = embedding / np.linalg.norm(embedding)
            
            # Store embedding with student ID
            embeddings[student_id] = embedding.tolist()
            print(f"✅ Processed ID: {student_id}")
        
        except Exception as e:
            print(f"❌ Error processing {img_path}: {e}")
    
    # Save embeddings to file
    with open(EMBEDDINGS_FILE, "w") as f:
        json.dump(embeddings, f, indent=4, ensure_ascii=False)
    
    print(f"\n💾 Embeddings saved to {EMBEDDINGS_FILE}")

if __name__ == "__main__":
    generate_embeddings()


