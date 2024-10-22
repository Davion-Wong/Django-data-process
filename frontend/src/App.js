import React, { useState } from 'react';
import axios from 'axios';  // Make sure Axios is imported

function App() {
    const [file, setFile] = useState(null);  // Initialize file state
    const [inferredTypes, setInferredTypes] = useState(null);  // Initialize inferredTypes state
    const [error, setError] = useState('');  // Initialize error state

    const handleFileChange = (e) => {
        setFile(e.target.files[0]);  // Set the selected file
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        if (!file) {
            setError('Please upload a file.');
            return;
        }

        const formData = new FormData();
        formData.append('file', file);

        try {
            const response = await axios.post('http://127.0.0.1:8000/data/api/upload/', formData, {
                headers: {
                    'Content-Type': 'multipart/form-data'
                }
            });
            setInferredTypes(response.data.inferred_types);
            setError('');
        } catch (err) {
            setError('File upload failed.');
            console.error(err);
        }
    };

    return (
        <div className="App">
            <h1>Upload CSV/Excel for Data Type Inference</h1>
            <form onSubmit={handleSubmit}>
                <input type="file" onChange={handleFileChange} accept=".csv, .xlsx" />
                <button type="submit">Upload</button>
            </form>

            {error && <p style={{ color: 'red' }}>{error}</p>}

            {inferredTypes && (
                <div>
                    <h2>Inferred Data Types:</h2>
                    <ul>
                        {Object.entries(inferredTypes).map(([column, dtype]) => (
                            <li key={column}>{column}: {dtype}</li>
                        ))}
                    </ul>
                </div>
            )}
        </div>
    );
}

export default App;
