const API_BASE = '/api/cats';

// Load recent cats on home page
async function loadRecentCats() {
    try {
        const response = await fetch(`${API_BASE}`);
        const cats = await response.json();
        
        const grid = document.getElementById('recent-cats-grid');
        if (!grid) return;
        
        if (cats.length === 0) {
            grid.innerHTML = '<p>No cats uploaded yet. Be the first!</p>';
            return;
        }
        
        // Show only first 6 cats
        const recentCats = cats.slice(0, 6);
        grid.innerHTML = recentCats.map(cat => createCatCard(cat)).join('');
    } catch (error) {
        console.error('Error loading recent cats:', error);
        const grid = document.getElementById('recent-cats-grid');
        if (grid) {
            grid.innerHTML = '<p>Error loading cats. Please try again later.</p>';
        }
    }
}

// Setup upload form
function setupUploadForm() {
    const form = document.getElementById('upload-form');
    const imageInput = document.getElementById('image');
    const imagePreview = document.getElementById('image-preview');
    const messageDiv = document.getElementById('upload-message');
    
    // Image preview
    imageInput.addEventListener('change', (e) => {
        const file = e.target.files[0];
        if (file) {
            const reader = new FileReader();
            reader.onload = (e) => {
                imagePreview.innerHTML = `<img src="${e.target.result}" alt="Preview">`;
            };
            reader.readAsDataURL(file);
        }
    });
    
    // Form submission
    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        const formData = new FormData(form);
        messageDiv.innerHTML = '<p>Uploading...</p>';
        messageDiv.className = 'message';
        
        try {
            const response = await fetch(`${API_BASE}/upload`, {
                method: 'POST',
                body: formData
            });
            
            const result = await response.json();
            
            if (response.ok) {
                messageDiv.innerHTML = '<p>Cat uploaded successfully! <a href="gallery.html">View Gallery</a></p>';
                messageDiv.className = 'message success';
                form.reset();
                imagePreview.innerHTML = '';
            } else {
                messageDiv.innerHTML = `<p>Error: ${result.detail || 'Upload failed'}</p>`;
                messageDiv.className = 'message error';
            }
        } catch (error) {
            console.error('Error uploading cat:', error);
            messageDiv.innerHTML = '<p>Error uploading cat. Please try again.</p>';
            messageDiv.className = 'message error';
        }
    });
}

// Load gallery
async function loadGallery() {
    try {
        const response = await fetch(`${API_BASE}`);
        const cats = await response.json();
        
        const grid = document.getElementById('cats-grid');
        const filterSelect = document.getElementById('filter-status');
        
        if (!grid) return;
        
        if (cats.length === 0) {
            grid.innerHTML = '<p>No cats uploaded yet. <a href="upload.html">Upload one now!</a></p>';
            return;
        }
        
        // Render all cats initially
        renderCats(cats);
        
        // Filter functionality
        if (filterSelect) {
            filterSelect.addEventListener('change', (e) => {
                const status = e.target.value;
                const filteredCats = status ? cats.filter(cat => cat.status === status) : cats;
                renderCats(filteredCats);
            });
        }
    } catch (error) {
        console.error('Error loading gallery:', error);
        const grid = document.getElementById('cats-grid');
        if (grid) {
            grid.innerHTML = '<p>Error loading cats. Please try again later.</p>';
        }
    }
}

// Render cats to grid
function renderCats(cats) {
    const grid = document.getElementById('cats-grid');
    if (!grid) return;
    
    if (cats.length === 0) {
        grid.innerHTML = '<p>No cats match the filter.</p>';
        return;
    }
    
    grid.innerHTML = cats.map(cat => createCatCard(cat)).join('');
}

// Create cat card HTML
function createCatCard(cat) {
    const statusClass = `status-${cat.status}`;
    const statusLabel = cat.status.charAt(0).toUpperCase() + cat.status.slice(1);
    
    return `
        <div class="cat-card">
            <img src="${cat.image_url}" alt="Cat" loading="lazy">
            <div class="cat-card-content">
                <span class="cat-status ${statusClass}">${statusLabel}</span>
                <p class="cat-location">📍 ${cat.location}</p>
                <p class="cat-description">${cat.description}</p>
                <div class="cat-card-actions">
                    <button onclick="findSimilar('${cat.id}')" class="btn btn-sm btn-primary">Find Similar</button>
                </div>
            </div>
        </div>
    `;
}

// Find similar cats
async function findSimilar(catId) {
    window.location.href = `similar.html?id=${catId}`;
}

// Load similar cats page
async function loadSimilarCats() {
    const urlParams = new URLSearchParams(window.location.search);
    const catId = urlParams.get('id');
    
    if (!catId) {
        window.location.href = 'gallery.html';
        return;
    }
    
    try {
        // Get target cat
        const targetResponse = await fetch(`${API_BASE}/${catId}`);
        const targetCat = await targetResponse.json();
        
        const targetDiv = document.getElementById('target-cat');
        if (targetDiv) {
            targetDiv.innerHTML = `
                <img src="${targetCat.image_url}" alt="Target Cat">
                <h3 style="margin-top: 1rem;">${targetCat.status.charAt(0).toUpperCase() + targetCat.status.slice(1)} - ${targetCat.location}</h3>
                <p>${targetCat.description}</p>
            `;
        }
        
        // Get similar cats
        const similarResponse = await fetch(`${API_BASE}/similar/${catId}`);
        const similarCats = await similarResponse.json();
        
        const grid = document.getElementById('similar-cats-grid');
        if (!grid) return;
        
        if (similarCats.length === 0) {
            grid.innerHTML = '<p>No similar cats found.</p>';
            return;
        }
        
        grid.innerHTML = similarCats.map(cat => createSimilarCatCard(cat)).join('');
    } catch (error) {
        console.error('Error loading similar cats:', error);
        const grid = document.getElementById('similar-cats-grid');
        if (grid) {
            grid.innerHTML = '<p>Error loading similar cats. Please try again later.</p>';
        }
    }
}

// Create similar cat card HTML
function createSimilarCatCard(cat) {
    const similarityPercentage = (cat.similarity_score * 100).toFixed(1);
    
    return `
        <div class="cat-card">
            <img src="${cat.image_url}" alt="Similar Cat" loading="lazy">
            <div class="cat-card-content">
                <p class="similarity-score">${similarityPercentage}% Match</p>
                <div class="cat-card-actions">
                    <button onclick="findSimilar('${cat.cat_id}')" class="btn btn-sm btn-secondary">Find Similar to This</button>
                </div>
            </div>
        </div>
    `;
}
