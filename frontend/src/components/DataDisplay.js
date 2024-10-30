import React, { useEffect, useState } from 'react';

function DataDisplay() {
    const [data, setData] = useState([]);
    const [types, setTypes] = useState({});
    const [page, setPage] = useState(1);
    const [taskId, setTaskId] = useState(null);
    const [processing, setProcessing] = useState(false);

    const pageSize = 10;

    // Function to fetch processed data
    const fetchProcessedData = async () => {
        try {
            const response = await fetch(`http://127.0.0.1:8000/data/api/dataset/?page=${page}&page_size=${pageSize}`);
            const result = await response.json();
            setData(result.results.data);
            setTypes(result.results.types);
        } catch (error) {
            console.error("Failed to fetch processed data:", error);
        }
    };

    // Function to check task status
    const checkTaskStatus = async (taskId) => {
        try {
            const response = await fetch(`http://127.0.0.1:8000/data/api/task-status/${taskId}/`);
            const result = await response.json();

            if (result.status === 'Completed') {
                setProcessing(false);
                fetchProcessedData();  // Reload processed data when task is complete
            } else if (result.status === 'In Progress' || result.status === 'Pending') {
                setTimeout(() => checkTaskStatus(taskId), 2000);  // Poll again after 2 seconds
            }
        } catch (error) {
            console.error("Failed to check task status:", error);
        }
    };

    // Function to handle file upload
    const handleFileUpload = async (event) => {
        const file = event.target.files[0];
        if (!file) return;

        const formData = new FormData();
        formData.append('file', file);

        try {
            const response = await fetch('http://127.0.0.1:8000/data/api/upload/', {
                method: 'POST',
                body: formData
            });
            const result = await response.json();
            if (result.task_id) {
                setTaskId(result.task_id);
                setProcessing(true);
                checkTaskStatus(result.task_id);  // Start checking task status after upload
            }
        } catch (error) {
            console.error("Failed to upload file:", error);
        }
    };

    // Initial load of processed data
    useEffect(() => {
        if (!processing) {
            fetchProcessedData();
        }
    }, [page, processing]);

    return (
        <div>
            <input type="file" onChange={handleFileUpload} />
            {processing && <p>Processing your file, please wait...</p>}
            <div>
                <h2>Processed Data:</h2>
                <table>
                    <thead>
                        <tr>
                            {Object.keys(data[0] || {}).map((header) => (
                                <th key={header}>{header}</th>
                            ))}
                        </tr>
                        <tr>
                            {Object.keys(types).map((typeKey) => (
                                <th key={typeKey}>Type: {types[typeKey]}</th>
                            ))}
                        </tr>
                    </thead>
                    <tbody>
                        {data.map((row, index) => (
                            <tr key={index}>
                                {Object.values(row).map((value, idx) => (
                                    <td key={idx}>{value}</td>
                                ))}
                            </tr>
                        ))}
                    </tbody>
                </table>
            </div>
            <button onClick={() => setPage(page - 1)} disabled={page === 1}>Previous</button>
            <span> Page {page} </span>
            <button onClick={() => setPage(page + 1)}>Next</button>
        </div>
    );
}

export default DataDisplay;
