// frontend/src/App.js

import React, { useEffect, useState } from 'react';
import axios from 'axios';

const App = () => {
    const [csrfToken, setCSRFToken] = useState(null);
    const [file, setFile] = useState(null);
    const [progress, setProgress] = useState(0);

    // Function to fetch CSRF Token
    const fetchCSRFToken = async () => {
        const response = await fetch("http://localhost:8000/data/api/csrf/", {
            credentials: 'include',
        });
        const data = await response.json();
        return data.csrfToken;
    };



    // Trigger CSRF fetch on component mount
    useEffect(() => {
        console.log("Fetching CSRF token...");
        fetchCSRFToken();
    }, []);

    // Handle file change
    const handleFileChange = (event) => {
        setFile(event.target.files[0]);
    };

    // Handle file upload
    const handleUpload = async (file) => {
        const csrfToken = await fetchCSRFToken();
        const formData = new FormData();
        formData.append("file", file);

        axios.post("http://localhost:8000/data/api/upload/", formData, {
            headers: {
                "X-CSRFToken": csrfToken,
            },
            withCredentials: true,
        }).then(response => {
            console.log("File uploaded successfully", response);
        }).catch(error => {
            console.error("File upload failed:", error);
        });
    };

    return (
        <div>
            <input
                type="file"
                onChange={(e) => handleUpload(e.target.files[0])}
            />
            <button onClick={handleUpload}>Upload File</button>
            <p>Upload Progress: {progress}%</p>
            <button onClick={fetchCSRFToken}>Fetch CSRF Token</button>
        </div>
    );
};

export default App;
