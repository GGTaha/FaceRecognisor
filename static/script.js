document.addEventListener('DOMContentLoaded', () => {
    const dropZone = document.getElementById('drop-zone');
    const fileInput = document.getElementById('file-input');
    const previewImg = document.getElementById('preview-img');
    const uploadPlaceholder = dropZone.querySelector('.upload-placeholder');

    // Result Elements
    const resultPlaceholder = document.getElementById('result-placeholder');
    const loader = document.getElementById('loader');
    const matchDetails = document.getElementById('match-details');
    const errorMessage = document.getElementById('error-message');

    const sisImg = document.getElementById('sis-img');
    const resName = document.getElementById('res-name');
    const resId = document.getElementById('res-id');
    const resConf = document.getElementById('res-conf');
    const confFill = document.getElementById('conf-fill');

    // --- Glow Effect ---
    const panels = document.querySelectorAll('.panel');
    panels.forEach(panel => {
        panel.addEventListener('mousemove', (e) => {
            const rect = panel.getBoundingClientRect();
            const x = e.clientX - rect.left;
            const y = e.clientY - rect.top;

            panel.style.setProperty('--mouse-x', `${x}px`);
            panel.style.setProperty('--mouse-y', `${y}px`);
        });
    });

    // --- Upload Interaction ---

    dropZone.addEventListener('click', () => fileInput.click());

    dropZone.addEventListener('dragover', (e) => {
        e.preventDefault();
        dropZone.classList.add('dragover');
    });

    dropZone.addEventListener('dragleave', (e) => {
        e.preventDefault();
        dropZone.classList.remove('dragover');
    });

    dropZone.addEventListener('drop', (e) => {
        e.preventDefault();
        dropZone.classList.remove('dragover');
        if (e.dataTransfer.files.length > 0) {
            handleFile(e.dataTransfer.files[0]);
        }
    });

    fileInput.addEventListener('change', () => {
        if (fileInput.files.length > 0) {
            handleFile(fileInput.files[0]);
        }
    });

    function handleFile(file) {
        if (!file.type.startsWith('image/')) return;

        // 1. Show Preview immediately
        const reader = new FileReader();
        reader.onload = (e) => {
            previewImg.src = e.target.result;
            previewImg.classList.remove('hidden');
            uploadPlaceholder.classList.add('hidden');
        };
        reader.readAsDataURL(file);

        // 2. Reset Result State & Show Loader
        resetResultState();
        loader.classList.remove('hidden');

        // 3. Upload & Process
        const formData = new FormData();
        formData.append('file', file);

        fetch('/upload', {
            method: 'POST',
            body: formData
        })
            .then(response => response.json())
            .then(async data => {
                // Fake a minimum delay for smoothness if request is too fast
                await new Promise(r => setTimeout(r, 800));

                loader.classList.add('hidden');

                if (data.success && data.match_found) {
                    showMatch(data);
                } else {
                    showError(data.error || "No match found in database.");
                }
            })
            .catch(err => {
                loader.classList.add('hidden');
                showError("Server connection failed.");
            });
    }

    function resetResultState() {
        resultPlaceholder.classList.add('hidden');
        loader.classList.add('hidden');
        matchDetails.classList.add('hidden');
        errorMessage.classList.add('hidden');
    }

    function showMatch(data) {
        matchDetails.classList.remove('hidden');

        resName.textContent = data.name;
        resId.textContent = `ID: ${data.id}`;
        resConf.textContent = `${data.confidence.toFixed(1)}% Confidence`;

        // Animate confidence bar
        setTimeout(() => {
            confFill.style.width = `${Math.min(data.confidence, 100)}%`;
        }, 100);

        // Load SIS Image
        loadSISImage(data.id);
    }

    function showError(msg) {
        errorMessage.classList.remove('hidden');
        document.getElementById('error-text').textContent = msg;
    }

    async function loadSISImage(id) {
        const baseUrl = 'https://sis.cedar.edu.pk/uploads/';
        const extensions = ['jpg', 'png', 'jpeg'];

        // Set a gentle loading state for the image itself if needed, or placeholder
        sisImg.src = '';

        for (const ext of extensions) {
            const url = `${baseUrl}${id}.${ext}`;
            try {
                const valid = await checkImage(url);
                if (valid) {
                    sisImg.src = url;
                    return;
                }
            } catch (e) { continue; }
        }

        // If fail
        sisImg.src = 'https://via.placeholder.com/300x300?text=No+Photo';
    }

    function checkImage(url) {
        return new Promise((resolve) => {
            const img = new Image();
            img.onload = () => resolve(true);
            img.onerror = () => resolve(false);
            img.src = url;
        });
    }
});
