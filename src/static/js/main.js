// Variables to store logo data
let currentLogoData = null;
let logoSource = null; // 'suggested' or 'uploaded'

// Document ready function
document.addEventListener('DOMContentLoaded', function() {
    console.log('DOM fully loaded');
    
    // Company logo finder
    const findLogoBtn = document.getElementById('findLogoBtn');
    if (findLogoBtn) {
        findLogoBtn.addEventListener('click', findLogoHandler);
    } else {
        console.error('Find logo button not found');
    }
    
    // Use logo button
    const useLogoBtn = document.getElementById('useLogoBtn');
    if (useLogoBtn) {
        useLogoBtn.addEventListener('click', function() {
            if (currentLogoData) {
                selectLogo(currentLogoData);
            }
        });
    }
    
    // Reject logo button
    const rejectLogoBtn = document.getElementById('rejectLogoBtn');
    if (rejectLogoBtn) {
        rejectLogoBtn.addEventListener('click', function() {
            document.getElementById('logoResults').classList.add('d-none');
            currentLogoData = null;
        });
    }
    
    // Logo upload
    const logoUpload = document.getElementById('logoUpload');
    if (logoUpload) {
        logoUpload.addEventListener('change', handleLogoUpload);
    }
    
    // Generate button
    const generateBtn = document.getElementById('generateBtn');
    if (generateBtn) {
        generateBtn.addEventListener('click', generateDocument);
        console.log('Generate button handler attached');
    } else {
        console.error('Generate button not found');
    }
});

// Logo finder handler
function findLogoHandler() {
    const companyName = document.getElementById('companyName').value.trim();
    
    if (!companyName) {
        alert('Please enter a company name');
        return;
    }
    
    // Show loading state
    const btnText = document.getElementById('findLogoBtnText');
    const spinner = document.getElementById('findLogoSpinner');
    btnText.textContent = 'Searching...';
    spinner.classList.remove('d-none');
    this.disabled = true;
    
    console.log('Fetching logo for:', companyName);
    
    // Call API to find logo
    fetch(`/find-logo?company=${encodeURIComponent(companyName)}`)
        .then(response => response.json())
        .then(data => {
            // Reset button state
            btnText.textContent = 'Find Logo';
            spinner.classList.add('d-none');
            this.disabled = false;
            
            console.log('Logo search result:', data);
            
            if (data.success && data.logoUrl) {
                // Show the found logos
                document.getElementById('logoResults').classList.remove('d-none');
                
                // Set the main logo
                const suggestedLogo = document.getElementById('suggestedLogo');
                suggestedLogo.src = data.logoUrl;
                suggestedLogo.dataset.originalUrl = data.logoUrl;
                currentLogoData = data.logoUrl;
                
                // Additional logo handling if needed
            } else {
                alert('Could not find a logo for this company. Please try another name or upload your own logo.');
            }
        })
        .catch(error => {
            btnText.textContent = 'Find Logo';
            spinner.classList.add('d-none');
            this.disabled = false;
            console.error('Error finding logo:', error);
            alert('Error: ' + error);
        });
}

// Logo selection handler
function selectLogo(logoUrl) {
    const preview = document.getElementById('logoPreview');
    const noLogoText = document.getElementById('noLogoText');
    
    preview.src = logoUrl;
    preview.classList.remove('d-none');
    noLogoText.classList.add('d-none');
    
    currentLogoData = logoUrl;
    logoSource = 'suggested';
    document.getElementById('logoResults').classList.add('d-none');
}

// Logo upload handler
function handleLogoUpload(event) {
    const file = event.target.files[0];
    const preview = document.getElementById('logoPreview');
    const noLogoText = document.getElementById('noLogoText');
    const label = document.querySelector('.custom-file-label');
    
    if (file) {
        label.textContent = file.name;
        
        const reader = new FileReader();
        reader.onload = function(e) {
            preview.src = e.target.result;
            preview.classList.remove('d-none');
            noLogoText.classList.add('d-none');
            currentLogoData = e.target.result;
            logoSource = 'uploaded';
        };
        reader.readAsDataURL(file);
    } else {
        preview.classList.add('d-none');
        noLogoText.classList.remove('d-none');
        label.textContent = 'Or upload your own logo...';
        currentLogoData = null;
        logoSource = null;
    }
}

// Generate document handler
function generateDocument() {
    console.log('Generate document function called');
    
    const jsonData = document.getElementById('jsonInput').value;
    if (!jsonData) {
        alert('Please enter JSON data');
        return;
    }
    
    const formData = new FormData();
    formData.append('json_data', jsonData);
    
    if (currentLogoData && logoSource) {
        if (logoSource === 'uploaded') {
            const logoFile = document.getElementById('logoUpload').files[0];
            if (logoFile) {
                formData.append('logo', logoFile);
                formData.append('logoSource', 'uploaded');
            }
        } else if (logoSource === 'suggested') {
            formData.append('logoUrl', currentLogoData);
            formData.append('logoSource', 'suggested');
        }
    }
    
    // Show loading indicator
    const generateBtn = document.getElementById('generateBtn');
    generateBtn.innerHTML = '<span class="spinner-border spinner-border-sm" role="status"></span> Generating...';
    generateBtn.disabled = true;
    
    console.log('Sending fetch request to /generate');
    
    fetch('/generate', {
        method: 'POST',
        body: formData
    })
    .then(response => {
        console.log('Response status:', response.status);
        if (!response.ok) {
            return response.text().then(text => { throw new Error(text) });
        }
        
        // Check if we got JSON (URL to file) or a file directly
        const contentType = response.headers.get('content-type');
        console.log('Response content-type:', contentType);
        
        if (contentType && contentType.includes('application/json')) {
            return response.json().then(data => {
                // Handle URL to file
                window.location.href = data.fileUrl;
            });
        } else {
            // Handle direct file download
            return response.blob().then(blob => {
                console.log('Got blob response, size:', blob.size);
                const url = window.URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.style.display = 'none';
                a.href = url;
                a.download = 'agenda.docx';
                document.body.appendChild(a);
                a.click();
                window.URL.revokeObjectURL(url);
                
                // Show download success message
                document.getElementById('downloadArea').classList.remove('d-none');
            });
        }
    })
    .catch(error => {
        console.error('Error generating document:', error);
        alert('Error generating document: ' + error.message);
    })
    .finally(() => {
        // Reset button state
        generateBtn.innerHTML = 'Generate Agenda';
        generateBtn.disabled = false;
    });
}