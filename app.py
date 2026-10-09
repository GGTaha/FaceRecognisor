from flask import Flask, render_template, request, jsonify, send_from_directory
import os
import time
from werkzeug.utils import secure_filename
from find import identify_face

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['FACES_FOLDER'] = 'faces'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max upload

# Ensure directories exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['FACES_FOLDER'], exist_ok=True)

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp', 'bmp'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/person-image/<person_id>')
def get_person_image(person_id):
    """Serve the reference image for a recognized person if available."""
    faces_dir = os.path.abspath(app.config['FACES_FOLDER'])
    if not os.path.exists(faces_dir) and os.path.exists('known_faces'):
        faces_dir = os.path.abspath('known_faces')

    if not os.path.exists(faces_dir):
        return jsonify({'error': 'Faces directory not found'}), 404

    # Search for matching person reference photo
    for ext in ['.jpg', '.jpeg', '.png', '.webp', '.gif', '.bmp']:
        candidate = f"{person_id}{ext}"
        candidate_path = os.path.join(faces_dir, candidate)
        if os.path.isfile(candidate_path):
            return send_from_directory(faces_dir, candidate)

    return jsonify({'error': 'Person image not found'}), 404

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'})
    
    file = request.files['file']
    
    if file.filename == '':
        return jsonify({'error': 'No selected file'})
    
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        # Add timestamp to avoid collisions
        unique_filename = f"{int(time.time())}_{filename}"
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
        file.save(filepath)
        
        try:
            # Process the image
            start_time = time.time()
            result = identify_face(filepath)
            end_time = time.time()
            
            duration = end_time - start_time
            print(f"⏱️ Analysis took {duration:.4f} seconds")
            
            if result:
                return jsonify(result)
            else:
                return jsonify({'success': False, 'error': 'Analysis failed'})
                
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)})

    return jsonify({'error': 'File type not allowed'})

if __name__ == '__main__':
    app.run(debug=True, port=5000)
