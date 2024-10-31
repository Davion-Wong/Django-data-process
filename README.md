# Django Data Processing Application

This application is a Django-based project with a React frontend designed to infer data types from a CSV file. It supports bulk file processing with Celery and Redis to handle large datasets asynchronously.

The application was developed to meet specific requirements outlined in the provided Project Overview, which guided functionality, scalability, and performance.

---

## Installation

### Prerequisites
- **Python 3.10**
- **Node.js and npm**
- **Redis**

### Setup Steps

1. **Clone the Repository:**
   ```bash
   git clone https://github.com/Davion-Wong/Django-data-process.git
   cd Django-data-process

2. **Backend Setup**

- **Set up a virtual environment:**
   ```bash
   python -m venv .venv   
- **Activate the virtual environment:**

    ```bash
    Copy code
    # On Windows
    .venv\Scripts\activate
    
    # On macOS/Linux
    source .venv/bin/activate
  
- **Install the required Python packages:**
    ```bash
    pip install -r requirements.txt 
    ```
  
    Typical packages in requirements.txt may include:<br>
    - **Django<br>**
    - **djangorestframework<br>**
    - **Celery<br>**
    - **Redis<br>**
    - **pandas<br>**
    - **numpy<br>**
  
3. **Frontend Setup**

- **Set up a virtual environment:**
   ```bash
   cd frontend
   npm install
  ```
    
4. **Prepare Data Files**

- **Two data files are provided in the data_files/ directory:<br>**
    - **sample_data.csv: This file has only 5 rows and is used for quick testing. Note that data type inference may not be accurate due to the limited data.<br>**
    - **large_test_file - 10k.csv: This file contains 10,000 rows and allows for accurate data type inference.<br>**

## Running the Application Locally
To run the application, open four separate terminals and follow these steps:
1. Start Redis Server
   - **Run Redis in the first terminal:**
       ```bash
        redis-server
      ```
2. Start Celery Worker
   - **In the second terminal, start the Celery worker:**
       ```bash
        celery -A data_inference worker --loglevel=info
      ```
3. Start Django Server
   - **In the third terminal, start the Django server:**
       ```bash
        python manage.py runserver
      ```
4. Start React Frontend
   - **In the fourth terminal, navigate to the frontend directory and start the React app:**
       ```bash
        cd frontend
        npm start
      ```

## Project Structure
The project structure is organized as follows:
```markdown
django-data-process/
├── backend/
│   ├── infer_data_types.py
│   └── utils.py
├── data_files/
│   ├── large_test_file - 10k.csv
│   └── sample_data.csv
├── data_inference/
│   ├── __init__.py
│   ├── asgi.py
│   ├── celery.py
│   ├── settings.py
│   ├── tasks.py
│   ├── urls.py
│   └── wsgi.py
├── data_processing/
│   ├── migrations/
│   │   ├── 0001_initial.py
│   │   └── __init__.py
│   ├── templates/
│   │   ├── data_display.html
│   │   └── upload.html
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── models.py
│   ├── tests.py
│   ├── urls.py
│   └── views.py
├── frontend/
│   ├── public/
│   │   ├── favicon.ico
│   │   ├── index.html
│   │   ├── logo192.png
│   │   ├── logo512.png
│   │   ├── manifest.json
│   │   └── robots.txt
│   └── src/
│       ├── components/
│       │   ├── DataDisplay.js
│       │   └── PaginationControls.js
│       ├── App.css
│       ├── App.js
│       ├── App.test.js
│       ├── index.css
│       ├── index.js
│       ├── logo.svg
│       ├── reportWebVitals.js
│       └── setupTests.js
├── temp/
│   ├── app.log
│   ├── db.sqlite3
│   └── dump.rdb
├── .gitignore
├── manage.py
└── README.md
```

## Key Functionalities and Requirements Met

- **Asynchronous File Processing: This project uses Celery and Redis to handle large file uploads asynchronously, which prevents the frontend from freezing during data processing.**

- **Data Type Inference:**

  - **Advanced Inference Logic: The backend employs infer_column_type to differentiate between dates, text, numeric, and categorical data. This function has been optimized to handle large datasets and infer types with over 90% accuracy.**
  - **Diverse Data Inference: Through testing with large_test_file - 10k.csv, the inference logic has been validated to correctly recognize various data types.**
- **Efficient Pagination and Display: The React frontend incorporates pagination to handle and display large datasets efficiently, using dynamic page sizes for user-friendly data exploration.**

- **Error Handling and Logging: The project includes robust error handling and logging (configured in app.log) for tracing and debugging, while minimizing verbosity to avoid excessive log generation.**

- **Simplified and Clean Codebase: Unnecessary files, functions, and logs have been removed to maintain a streamlined codebase, ensuring ease of navigation and maintenance.**

## Future Improvements
- **Enhanced Data Type Recognition: Further optimizations could allow for even finer distinctions in data type categorization, especially for mixed-type columns.**

- **Improved Frontend User Experience: Adding loading animations and improved error messages in the frontend for better feedback during file processing.**