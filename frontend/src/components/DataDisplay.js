import React, { useEffect, useState, useCallback } from 'react';
import axios from 'axios';

function DataDisplay() {
    const [data, setData] = useState([]);
    const [types, setTypes] = useState({});
    const [page, setPage] = useState(1);
    const [processing, setProcessing] = useState(false);
    const [error, setError] = useState(null);
    const [dataReady, setDataReady] = useState(false);

    const pageSize = 10;

    // Polling function to check if data is ready
    const pollTaskStatus = async (taskId) => {
        try {
            const response = await axios.get(`http://127.0.0.1:8000/data/api/task-status/${taskId}/`);
            const { status } = response.data;

            if (status === "Completed") {
                setProcessing(false);
                // After completion, confirm that processed data is ready
                const dataStatus = await axios.get('http://127.0.0.1:8000/data/api/processed_data_status/');
                if (dataStatus.data.processed_data_ready) {
                    setDataReady(true);  // Only then mark data as ready
                    fetchProcessedData();  // Call to fetch the data immediately after ready
                }
            } else if (status === "Failed") {
                setProcessing(false);
                setError("File processing failed.");
            } else {
                setTimeout(() => pollTaskStatus(taskId), 2000);  // Continue polling
            }
        } catch (error) {
            console.error("Failed to check task status:", error);
        }
    };


    // Function to fetch the processed data
    const fetchProcessedData = async () => {
        console.log("Fetching processed data...");
        try {
            const response = await fetch(`http://127.0.0.1:8000/data/api/dataset/?page=${page}&page_size=${pageSize}`);
            const result = await response.json();
            console.log("Data fetched:", result); // Log the fetched data

            if (response.ok) {
                setData(result.results.data);
                setTypes(result.results.types);
                setError(null);  // Clear any previous errors
            } else {
                // Handle cases where data is not available or there's an error
                setError("No processed data available. Please upload a file first.");
                setData([]);  // Clear data if there's no processed data file
                setTypes({});
            }
        } catch (err) {
            console.error("Failed to fetch processed data:", err);
            setError("Failed to fetch processed data.");
        }
    };

    // Handle file upload and initiate processing
    const handleFileUpload = async (event) => {
        const file = event.target.files[0];
        if (!file) return;

        const formData = new FormData();
        formData.append('file', file);

        try {
            const response = await axios.post('http://127.0.0.1:8000/data/api/upload/', formData);
            const { task_id } = response.data;
            if (task_id) {
                setProcessing(true);
                setDataReady(false);
                pollTaskStatus(task_id);  // Start polling the task status
            }
        } catch (error) {
            console.error("Failed to upload file:", error);
            setError("Failed to upload file.");
        }
    };

    useEffect(() => {
        console.log("Data ready status:", dataReady);
        if (dataReady) {
            fetchProcessedData();
        }
    }, [dataReady, page]);

    return (
        <div className="data-container">
            <h3>Choose your CSV file here:</h3>
            <input type="file" onChange={handleFileUpload} />
            {processing && <p>Processing your file, please wait...</p>}
            {error && <p className="error">{error}</p>}
            <div>
                <h3>Processed Data:</h3>
                {data.length > 0 ? (
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
                ) : (
                    <p>No data available.</p>
                )}
            </div>
            <div className="pagination-controls">
                <button onClick={() => setPage(page - 1)} disabled={page === 1}>Previous</button>
                <span> Page {page} </span>
                <button onClick={() => setPage(page + 1)}>Next</button>
            </div>
        </div>
    );
}

export default DataDisplay;
