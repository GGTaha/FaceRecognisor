# Face Recognition App

## Setup Instructions

To run this application on a new machine, follow these steps:

### 1. Prerequisites
*   **Python 3.10 or 3.11** is recommended.
*   **Microsoft Visual C++ Redistributable**: REQUIRED for TensorFlow on Windows.
    *   Download and install: [https://aka.ms/vs/17/release/vc_redist.x64.exe](https://aka.ms/vs/17/release/vc_redist.x64.exe)

### 2. Installation
Open a terminal in this folder and run:

```bash
pip install -r requirements.txt
```

### 3. Usage
1.  Run the application:
    ```bash
    python app.py
    ```
2.  Open your browser to: `http://127.0.0.1:5000`

### Files
*   `app.py`: The Flask web server.
*   `find.py`: The face recognition logic.
*   `embeddings.json`: The database of known faces (do not delete!).
*   `student_data_full.json`: The list of student names/IDs.
