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

    const personImg = document.getElementById('person-img');
    const resName = document.getElementById('res-name');
    const resId = document.getElementById('res-id');
    const resConf = document.getElementById('res-conf');
    const confFill = document.getElementById('conf-fill');

    // Default Avatar SVG Data URI
    const DEFAULT_AVATAR = 'data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="%2364748b"><path d="M12 12c2.21 0 4-1.79 4-4s-1.79-4-4-4-4 1.79-4 4 1.79 4 4 4zm0 2c-2.67 0-8 1.34-8 4v2h16v-2c0-2.66-5.33-4-8-4z"/></svg>';

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
                // Minimum delay for smoother UX
                await new Promise(r => setTimeout(r, 600));

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

        // Load Person Reference Image
        loadPersonImage(data.id);
    }

    function showError(msg) {
        errorMessage.classList.remove('hidden');
        document.getElementById('error-text').textContent = msg;
    }

    function loadPersonImage(personId) {
        personImg.src = DEFAULT_AVATAR;
        const targetUrl = `/person-image/${encodeURIComponent(personId)}`;

        const img = new Image();
        img.onload = () => {
            personImg.src = targetUrl;
        };
        img.onerror = () => {
            personImg.src = DEFAULT_AVATAR;
        };
        img.src = targetUrl;
    }
});
