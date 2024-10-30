import React, { useEffect, useState } from 'react';
import axios from 'axios';
import DataDisplay from './components/DataDisplay';
import './App.css';

const App = () => {
    const [csrfToken, setCSRFToken] = useState(null);
    const [file, setFile] = useState(null);
    const [progress, setProgress] = useState("");
    const [data, setData] = useState([]);

    const fetchCSRFToken = async () => {
        const response = await fetch("http://localhost:8000/data/api/csrf/", {
            credentials: 'include',
        });
        const data = await response.json();
        setCSRFToken(data.csrfToken);
    };

    useEffect(() => {
        console.log("Fetching CSRF token...");
        fetchCSRFToken();
    }, []);

    const handleFileChange = (event) => {
        setFile(event.target.files[0]);
    };

    const handleUpload = async () => {
        if (!file) {
            console.error("No file selected");
            return;
        }

        const formData = new FormData();
        formData.append("file", file);

        try {
            const uploadResponse = await axios.post("http://localhost:8000/data/api/upload/", formData, {
                headers: {
                    "X-CSRFToken": csrfToken,
                },
                withCredentials: true,
            });

            console.log("File uploaded successfully", uploadResponse);
            const { task_id } = uploadResponse.data;

            // Start polling for progress updates every second
            const intervalId = setInterval(async () => {
                const progressResponse = await axios.get(`http://localhost:8000/data/api/task-status/${task_id}/`);
                setProgress(`Upload Progress: ${progressResponse.data.progress.toFixed(2)}%`);

                if (progressResponse.data.progress === 100) {
                    setProgress("Upload finished, processing now");
                    clearInterval(intervalId); // Stop polling when complete
                    fetchProcessedData(); // Fetch processed data when done
                }
            }, 1000);
        } catch (error) {
            console.error("File upload failed:", error);
        }
    };

    const fetchProcessedData = () => {
        axios.get("http://localhost:8000/data/api/dataset/", {
            headers: {
                "X-CSRFToken": csrfToken,
            },
            withCredentials: true,
        })
        .then(response => {
            console.log("Processed data fetched", response.data);
            setData(response.data.results);  // Assuming paginated response
        })
        .catch(error => {
            console.error("Failed to fetch processed data:", error);
        });
    };

    return (
        <div>
            <div>
                <h2>Data Type Inference Application</h2>
                <DataDisplay />
            </div>
        </div>
    );
};

export default App;
