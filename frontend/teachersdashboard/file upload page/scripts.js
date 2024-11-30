// Handle file selection and display the file list dynamically
document.getElementById('pdfFiles').addEventListener('change', () => {
    const fileInput = document.getElementById('pdfFiles');
    const fileListDiv = document.getElementById('fileList');
  
    // Clear any previously displayed file list
    fileListDiv.innerHTML = '';
  
    // Check if any files are selected
    if (fileInput.files.length > 0) {
      Array.from(fileInput.files).forEach(file => {
        const fileItem = document.createElement('p');
        fileItem.innerHTML = `<i class="fas fa-file-pdf"></i> ${file.name}`;
        fileListDiv.appendChild(fileItem);
      });
    }
  });
  
  // Handle file upload
  document.getElementById('uploadBtn').addEventListener('click', () => {
    const fileInput = document.getElementById('pdfFiles');
    const dashboardBtn = document.getElementById('dashboardBtn');
  
    if (fileInput.files.length > 0) {
      alert('Files uploaded successfully!');
      dashboardBtn.style.display = 'block'; // Show the dashboard button
    } else {
      alert('Please select at least one PDF file!');
    }
  });
  
 // Redirect to the dashboard page
// Redirect to the dashboard page
    document.getElementById('dashboardBtn').addEventListener('click', () => {
        window.location.href = '../dashboard/dashboard.html'; // Adjusted path
    });
  