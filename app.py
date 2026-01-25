from flask import Flask, render_template, request, jsonify
import os
import time
from werkzeug.utils import secure_filename
from find import identify_face

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max upload

# Ensure upload directory exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

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
            
            # Clean up the uploaded file after processing
            # os.remove(filepath)
            
            if result:
                return jsonify(result)
            else:
                return jsonify({'success': False, 'error': 'Analysis failed'})
                
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)})

    return jsonify({'error': 'File type not allowed'})

if __name__ == '__main__':
    app.run(debug=True, port=5000)
