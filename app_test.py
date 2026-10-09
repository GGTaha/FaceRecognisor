from flask import Flask, render_template, request, jsonify, send_from_directory
import os
import time

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['FACES_FOLDER'] = 'faces'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['FACES_FOLDER'], exist_ok=True)

# MOCK FUNCTION - No deepface dependency
def identify_face_mock(filepath):
    time.sleep(1)  # Simulate processing
    return {
        "success": True,
        "match_found": True,
        "id": "person_sample",
        "name": "Sample Person (Mock)",
        "confidence": 98.5,
        "similarity": 0.85
    }

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/person-image/<person_id>')
def get_person_image(person_id):
    faces_dir = os.path.abspath(app.config['FACES_FOLDER'])
    if os.path.exists(faces_dir):
        for ext in ['.jpg', '.jpeg', '.png', '.webp', '.gif', '.bmp']:
            candidate = f"{person_id}{ext}"
            candidate_path = os.path.join(faces_dir, candidate)
            if os.path.isfile(candidate_path):
                return send_from_directory(faces_dir, candidate)
    return jsonify({'error': 'Image not found'}), 404

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'})
    
    file = request.files['file']
    
    if file.filename == '':
        return jsonify({'error': 'No selected file'})
    
    # Just return success for any file in test mode
    if file:
        result = identify_face_mock("dummy_path")
        return jsonify(result)

    return jsonify({'error': 'File type not allowed'})

if __name__ == '__main__':
    print("RUNNING IN TEST MODE (No DeepFace)")
    app.run(debug=True, port=5000)
