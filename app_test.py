from flask import Flask, render_template, request, jsonify
import os
import time

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# MOCK FUNCTION - No deepface dependency
def identify_face_mock(filepath):
    time.sleep(1) # Simulate processing
    return {
        "success": True,
        "match_found": True,
        "id": "123456",
        "name": "Test Student (Mock)",
        "confidence": 98.5,
        "similarity": 0.85
    }

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'})
    
    file = request.files['file']
    
    if file.filename == '':
        return jsonify({'error': 'No selected file'})
    
    # Just return success for any file in test mode
    if file:
        # Mock response
        result = identify_face_mock("dummy_path")
        return jsonify(result)

    return jsonify({'error': 'File type not allowed'})

if __name__ == '__main__':
    print("RUNNING IN TEST MODE (No DeepFace)")
    app.run(debug=True, port=5000)
