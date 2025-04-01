// Initialize CodeMirror globally
let editor;

// Document ready function
document.addEventListener('DOMContentLoaded', function() {
    console.log('DOM fully loaded');
    
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

    // Initialize CodeMirror for JSON input
    const jsonInput = document.getElementById('jsonInput');
    if (jsonInput) {
        editor = CodeMirror.fromTextArea(jsonInput, {
            mode: 'application/json',
            lineNumbers: true,
            matchBrackets: true,
            autoCloseBrackets: true,
            theme: 'default',
            viewportMargin: Infinity // Ensures the editor expands with content
        });

        // Add a button to format JSON
        const formatBtn = document.createElement('button');
        formatBtn.textContent = 'Format JSON';
        formatBtn.className = 'btn btn-secondary mt-2';
        formatBtn.addEventListener('click', () => {
            try {
                const formatted = JSON.stringify(JSON.parse(editor.getValue()), null, 4);
                editor.setValue(formatted);
            } catch (e) {
                alert('Invalid JSON: ' + e.message);
            }
        });

        // Append the button to the CodeMirror container
        const wrapper = editor.getWrapperElement();
        wrapper.parentNode.appendChild(formatBtn);
    }
});

// Logo upload handler
function handleLogoUpload(event) {
    const file = event.target.files[0];
    const preview = document.getElementById('logoPreview');
    const noLogoText = document.getElementById('noLogoText');
    const label = document.querySelector('.custom-file-label');
    
    if (file) {
        // Validate file is an image
        if (!file.type.match('image.*')) {
            alert('Please select an image file (PNG, JPG, GIF)');
            event.target.value = '';  // Clear the file input
            return;
        }
        
        // Check file size (max 5MB)
        if (file.size > 5 * 1024 * 1024) {
            alert('Logo file is too large. Please select an image under 5MB.');
            event.target.value = '';  // Clear the file input
            return;
        }
        
        label.textContent = file.name;
        
        const reader = new FileReader();
        reader.onload = function(e) {
            preview.src = e.target.result;
            preview.classList.remove('d-none');
            noLogoText.classList.add('d-none');
            
            // Verify image loaded correctly
            preview.onload = function() {
                console.log('Logo preview loaded successfully');
            };
            
            preview.onerror = function() {
                console.error('Error loading logo preview');
                alert('The selected file could not be loaded as an image. Please try another file.');
                event.target.value = '';  // Clear the file input
                preview.classList.add('d-none');
                noLogoText.classList.remove('d-none');
            };
        };
        reader.readAsDataURL(file);
    } else {
        preview.classList.add('d-none');
        noLogoText.classList.remove('d-none');
        label.textContent = 'Upload a logo image...';
    }
}

// Generate document handler
function generateDocument() {
    console.log('Generate document function called');
    
    try {
        // Retrieve JSON data from the global CodeMirror editor
        const jsonData = editor.getValue();
        
        if (!jsonData.trim()) {
            alert('Please enter JSON data');
            return;
        }
        
        // Validate JSON before submitting
        try {
            JSON.parse(jsonData);
        } catch (e) {
            alert('Invalid JSON format: ' + e.message);
            return;
        }
        
        const formData = new FormData();
        formData.append('json_data', jsonData);
        
        // Add logo if available
        const logoUpload = document.getElementById('logoUpload');
        const logoFile = logoUpload?.files[0];
        if (logoFile) {
            console.log('Adding logo file to request:', logoFile.name, 'Size:', logoFile.size);
            
            // Double-check file type
            if (!logoFile.type.match('image.*')) {
                console.warn('File does not appear to be an image:', logoFile.type);
                if (!confirm('The selected logo file may not be an image. Continue anyway?')) {
                    generateBtn.innerHTML = 'Generate Agenda';
                    generateBtn.disabled = false;
                    return;
                }
            }
            
            formData.append('logo', logoFile);
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
            if (!response.ok) {
                return response.text().then(text => {
                    throw new Error(text || `Server returned ${response.status}: ${response.statusText}`);
                });
            }
            
            console.log('Received response, status:', response.status);
            
            // Handle direct file download
            return response.blob().then(blob => {
                console.log('Got blob response, size:', blob.size);
                
                // Extract the filename from the Content-Disposition header
                let filename = 'agenda.docx';  // Default fallback
                const disposition = response.headers.get('Content-Disposition');
                if (disposition) {
                    console.log('Content-Disposition header:', disposition);
                    // Try to extract the filename
                    const filenameMatch = disposition.match(/filename="(.+?)"/i);
                    if (filenameMatch && filenameMatch[1]) {
                        filename = filenameMatch[1];
                        console.log('Extracted filename:', filename);
                    }
                }
                
                const url = window.URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.style.display = 'none';
                a.href = url;
                a.download = filename;
                document.body.appendChild(a);
                a.click();
                window.URL.revokeObjectURL(url);
                
                // Show download success message
                document.getElementById('downloadArea').classList.remove('d-none');
                
                // Reset generate button
                generateBtn.innerHTML = 'Generate Agenda';
                generateBtn.disabled = false;
            });
        })
        .catch(error => {
            console.error('Error generating document:', error);
            alert(`Error generating document: ${error.message}`);
            
            // Reset generate button
            generateBtn.innerHTML = 'Generate Agenda';
            generateBtn.disabled = false;
        });
    } catch (error) {
        console.error('Unexpected error in generate function:', error);
        alert('An unexpected error occurred: ' + error.message);
        
        // Reset generate button
        const generateBtn = document.getElementById('generateBtn');
        if (generateBtn) {
            generateBtn.innerHTML = 'Generate Agenda';
            generateBtn.disabled = false;
        }
    }
}