import React, { useState } from 'react';
import axios from 'axios';

function App() {
    const [file, setFile] = useState(null);
    const [data, setData] = useState([]);
    const [loading, setLoading] = useState(false);
    const [view, setView] = useState('upload'); // Track view: 'upload' or 'display'

    const handleFileChange = (event) => {
        setFile(event.target.files[0]);
    };

    const handleUpload = async () => {
        if (!file) {
            alert("Please select a file first!");
            return;
        }

        setLoading(true);
        const formData = new FormData();
        formData.append('file', file);

        try {
            await axios.post("http://127.0.0.1:8000/data/api/upload/", formData);
            alert("File uploaded successfully!");
            // Fetch first page of data after successful upload
            const response = await axios.get("http://127.0.0.1:8000/data/api/dataset/?page=1");
            setData(response.data.results);
            setView('display'); // Switch to display view
        } catch (err) {
            alert("File upload failed.");
        } finally {
            setLoading(false);
        }
    };

    if (loading) {
        return <div>Loading...</div>;
    }

    if (view === 'upload') {
        return (
            <div>
                <h1>Upload Dataset</h1>
                <input type="file" onChange={handleFileChange} />
                <button onClick={handleUpload}>Upload</button>
            </div>
        );
    }

    return (
        <div>
            <h1>Dataset</h1>
            <table>
                <thead>
                    <tr>
                        <th>Name</th>
                        <th>Birthdate</th>
                        <th>Score</th>
                        <th>Grade</th>
                        <th>Comments</th>
                    </tr>
                </thead>
                <tbody>
                    {data.map((item, index) => (
                        <tr key={index}>
                            <td>{item.Name}</td>
                            <td>{item.Birthdate}</td>
                            <td>{item.Score}</td>
                            <td>{item.Grade}</td>
                            <td>{item.Comments}</td>
                        </tr>
                    ))}
                </tbody>
            </table>
        </div>
    );
}

export default App;
