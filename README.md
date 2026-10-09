# Face Recognition & Identity Verification

A general-purpose, self-contained facial biometric identification system built with Flask, DeepFace (ArcFace & RetinaFace), and a glassmorphic web interface.

---

## Getting Started

### 1. Prerequisites
* **Python 3.10 or 3.11** is recommended.
* **Microsoft Visual C++ Redistributable**: Required for TensorFlow on Windows.
  * Download: [https://aka.ms/vs/17/release/vc_redist.x64.exe](https://aka.ms/vs/17/release/vc_redist.x64.exe)

### 2. Installation
Open a terminal in the project directory and install dependencies:

```bash
pip install -r requirements.txt
```

---

## Workflow & Usage

### Step 1: Add Reference Photos
Place reference photos of known persons in the `faces/` directory:
```
faces/
  ├── elon_musk.jpg
  ├── marie_curie.png
  └── ada_lovelace.jpg
```
The filename (without the extension) is automatically used as the person's identifier and display name.

### Step 2 (Optional): Custom Nicknames / Display Names
If you wish to map filenames to friendly display names or nicknames, create an optional `names.json` file in the root folder:

```json
{
  "elon_musk": "Elon Musk",
  "marie_curie": "Marie Curie",
  "ada_lovelace": "Ada Lovelace"
}
```
*Note: If `names.json` is not provided or a person is not listed, the system defaults to using the image file name.*

### Step 3: Generate Embeddings
Run the setup script to generate vector embeddings for all photos:

```bash
python setup.py
```
This detects faces using **RetinaFace**, extracts 512-dimensional normalized embeddings using **ArcFace**, and saves them to `embeddings.json`.

### Step 4: Run the Web Server
Launch the Flask application:

```bash
python app.py
```
Open your browser and navigate to: `http://127.0.0.1:5000`

---

## Fast UI Testing Mode (No TensorFlow Required)
To test the web interface without loading deep learning models:

```bash
python app_test.py
```

---

## Project Structure
* `setup.py`: Generates precomputed vector embeddings from photos in `faces/`.
* `find.py`: Performs runtime biometric face representation and cosine similarity matching.
* `app.py`: Flask web application providing the upload API and reference image serving.
* `app_test.py`: Mock web server for testing UI interactions without heavy ML dependencies.
* `faces/`: Folder storing reference images of known persons.
* `names.json`: (Optional) Custom nickname and display name mapping file.
* `templates/index.html`: Responsive biometric identity verification dashboard.
* `static/script.js`: Interactive drag-and-drop and API communication logic.
* `static/style.css`: Modern glassmorphic dark-mode styling.
