// App.js

import axios from 'axios';
import { useEffect, useState } from 'react';


const handleUpload = async (event) => {
    event.preventDefault();
    const formData = new FormData();
    formData.append('file', event.target.files[0]); // Adjust if necessary

    try {
        const response = await axios.post("http://127.0.0.1:8000/data/api/upload/", formData, {
            headers: {
                'X-CSRFToken': getCSRFToken(),
            },
            withCredentials: true
        });
        console.log("File uploaded successfully:", response.data); // Check the response data here
    } catch (error) {
        console.error("File upload failed:", error);
    }

    axios.post("http://127.0.0.1:8000/data/api/upload/", formData, {
        headers: {
            'X-CSRFToken': getCSRFToken(),
        },
        withCredentials: true
    })
    .then(response => {
        // Handle success
    })
    .catch(error => {
        // Handle error
    });
};




function getCSRFToken() {
    const name = 'csrftoken';
    const cookies = document.cookie.split(';');
    for (let i = 0; i < cookies.length; i++) {
        const cookie = cookies[i].trim();
        if (cookie.startsWith(name + '=')) {
            return cookie.substring(name.length + 1);
        }
    }
    return null;
}

function App() {
    const [file, setFile] = useState(null);
    const [progress, setProgress] = useState(0);
    const [taskId, setTaskId] = useState(null);

    const handleFileChange = (event) => {
        setFile(event.target.files[0]);
    };

    const handleUpload = async () => {
        if (!file) return;

        const formData = new FormData();
        formData.append('file', file);

        try {
            // Upload file and start the task
            const response = await axios.post('http://127.0.0.1:8000/data/api/upload/', formData, {
                headers: {
                    'Content-Type': 'multipart/form-data',
                    'X-CSRFToken': getCSRFToken(),  // Make sure you have a function to retrieve the CSRF token
                },
                withCredentials: true,
            });

            setTaskId(response.data.task_id);  // Retrieve task ID after upload
            pollProgress(response.data.task_id);  // Start polling progress
        } catch (error) {
            console.error('File upload failed:', error);
        }
    };

    const pollProgress = (taskId) => {
        const interval = setInterval(async () => {
            try {
                const response = await axios.get(`http://127.0.0.1:8000/data/api/task-progress/${taskId}/`);
                setProgress(response.data.progress);
                if (response.data.progress >= 100) clearInterval(interval);
            } catch (error) {
                console.error('Progress check failed:', error);
            }
        }, 1000);
    };

    return (
        <div>
            <input type="file" onChange={handleFileChange} />
            <button onClick={handleUpload}>Upload and Start Task</button>
            <p>Task Progress: {progress}%</p>
        </div>
    );
}

export default App;
