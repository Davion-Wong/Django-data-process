// In App.js (React Frontend)

import React, { useState, useEffect } from "react";
import axios from "axios";

function App() {
    const [taskId, setTaskId] = useState(null);
    const [progress, setProgress] = useState(0);
    const [status, setStatus] = useState("");

    const handleSubmit = async (e) => {
        e.preventDefault();
        const file = e.target.elements.file.files[0];
        const formData = new FormData();
        formData.append("file", file);

        try {
            const response = await axios.post("http://127.0.0.1:8000/data/api/upload/", formData);
            setTaskId(response.data.task_id);
            setStatus("Processing file...");
        } catch (error) {
            console.error("File upload failed:", error);
        }
    };

    useEffect(() => {
        if (taskId) {
            const interval = setInterval(async () => {
                const response = await axios.get(`http://127.0.0.1:8000/data/api/task-progress/${taskId}/`);
                setProgress(response.data.progress);
                if (response.data.progress === 100) {
                    setStatus("Processing complete!");
                    clearInterval(interval);
                }
            }, 1000); // Poll every second
            return () => clearInterval(interval);
        }
    }, [taskId]);

    return (
        <div>
            <h1>Upload and Process File</h1>
            <form onSubmit={handleSubmit}>
                <input type="file" name="file" />
                <button type="submit">Upload</button>
            </form>
            {status && <p>{status}</p>}
            {progress > 0 && <p>Progress: {progress}%</p>}
        </div>
    );
}

export default App;
