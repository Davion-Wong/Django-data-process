import React, { useState } from 'react';
import axios from 'axios';

function App() {
  const [file, setFile] = useState(null);
  const [error, setError] = useState('');

  const getCSRFToken = () => {
    let csrfToken = null;
    const cookies = document.cookie.split(';');
    cookies.forEach((cookie) => {
      const [key, value] = cookie.trim().split('=');
      if (key === 'csrftoken') {
        csrfToken = value;
      }
    });
    return csrfToken;
  };

  const handleFileChange = (e) => {
    setFile(e.target.files[0]);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    const formData = new FormData();
    formData.append('file', file);

    try {
      const response = await axios.post('/data/api/upload/', formData, {
        headers: {
          'X-CSRFToken': getCSRFToken(),  // Pass CSRF token with the request
        },
      });
      alert('File uploaded successfully');
    } catch (err) {
      setError('File upload failed.');
    }
  };

  return (
    <div>
      <h1>Upload Your Data File</h1>

      <form onSubmit={handleSubmit}>
        <input type="file" onChange={handleFileChange} accept=".csv, .xlsx" />
        <button type="submit">Upload File</button>
      </form>

      {error && <p>{error}</p>}
    </div>
  );
}

export default App;
