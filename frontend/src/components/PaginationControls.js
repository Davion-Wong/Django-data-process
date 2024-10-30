let currentPage = 1;
const pageSize = 10;

async function fetchPaginatedData(page = 1) {
    try {
        const response = await fetch(`http://127.0.0.1:8000/data/get-processed-dataset/?page=${page}&page_size=${pageSize}`);
        if (!response.ok) throw new Error('Failed to fetch data');

        const data = await response.json();
        displayData(data.results);
        updatePaginationControls(data);
    } catch (error) {
        console.error('Error fetching paginated data:', error);
        document.getElementById('data-container').innerHTML = '<p>Error loading data.</p>';
    }
}

function displayData(data) {
    const dataContainer = document.getElementById('data-container');
    dataContainer.innerHTML = ''; // Clear previous data

    data.forEach(item => {
        const listItem = document.createElement('li');
        listItem.textContent = JSON.stringify(item);
        dataContainer.appendChild(listItem);
    });
}

function updatePaginationControls(data) {
    document.getElementById('pagination-info').textContent = `Page ${data.current_page} of ${Math.ceil(data.count / pageSize)}`;

    document.getElementById('prev-button').disabled = !data.previous;
    document.getElementById('next-button').disabled = !data.next;
}

function goToNextPage() {
    currentPage++;
    fetchPaginatedData(currentPage);
}

function goToPreviousPage() {
    if (currentPage > 1) {
        currentPage--;
        fetchPaginatedData(currentPage);
    }
}

document.addEventListener('DOMContentLoaded', () => fetchPaginatedData());
