# Custom Job Queue System with Streamlit Tester

This project implements a custom job queue system with a REST API (Flask), a worker process for job processing, and a Streamlit application for testing. The system supports job prioritization, retries with exponential backoff, timestamp tracking, and status checking, using Redis for queue storage without relying on off-the-shelf task queue libraries like Celery or RQ. It can be run locally or using Docker for easy setup.

## Project Overview

- **Components**:
  - **Flask API (`api.py`)**: Provides endpoints to submit jobs (`/submit-job`) and check job status (`/jobs/status/<job_id>`).
  - **Worker (`worker.py`)**: Polls the Redis queue, processes jobs (mock email sending), handles retries, and logs timestamps.
  - **Streamlit App (`app.py`)**: A web interface to submit jobs, check statuses, and view simulated worker logs.
  - **Requirements (`requirements.txt`)**: Lists Python dependencies.
  - **Dockerfile and docker-compose.yml**: Containerize the application for easy deployment.
- **Features**:
  - Job prioritization: High-priority jobs (`priority: high`) processed before low-priority jobs (`priority: low`).
  - Retries: Up to 3 attempts with exponential backoff (2^n seconds) for failed jobs.
  - Timestamps: Tracks `created_at`, `picked_at`, `completed_at`/`failed_at`.
  - Status endpoint: Retrieves job details by ID.
  - Streamlit interface: Simplifies testing with a user-friendly UI.

## Prerequisites

To run the application, ensure the following are installed:

1. **Docker (Recommended for Easy Setup)**:
   - Install [Docker Desktop for Windows](https://www.docker.com/products/docker-desktop/).
   - Verify:
     ```cmd
     docker --version
     ```
     Example output: `Docker version 20.10.0`
   - Start Docker Desktop before proceeding.

2. **Python 3.8 or higher (For Local Setup)**:
   - Download from [python.org](https://www.python.org/downloads/).
   - Check "Add Python to PATH" during installation.
   - Verify:
     ```cmd
     python --version
     ```
     Example output: `Python 3.8.0`

3. **Redis (For Local Setup)**:
   nums
   - **Option 1: Docker** (included in `docker-compose.yml`).
   - **Option 2: Memurai (Windows-native Redis)**:
     - Download from [memurai.com](https://www.memurai.com/).
     - Install and start Memurai.
   - Verify Redis:
     ```cmd
     redis-cli -h localhost -p 6379 ping
     ```
     Expected output: `PONG`

4. **Windows 10/11**:
   - The application is tested on Windows, using Command Prompt commands.

5. **Project Files**:
   - Ensure the following files are in `C:\job_queue_system`:
     - `api.py`
     - `worker.py`
     - `app.py`
     - `requirements.txt`
     - `Dockerfile`
     - `docker-compose.yml`
     - `README.md`

## Setup Instructions

### Option 1: Run with Docker (Recommended)

Docker simplifies setup by managing Redis and all application components.

1. **Create Project Directory**:
   - Create a folder at `C:\job_queue_system`.
   - Place all project files in this directory.

2. **Build and Run with Docker Compose**:
   - Open Command Prompt.
   - Navigate to the project directory:
     ```cmd
     cd C:\job_queue_system
     ```
   - Build and start all services (Redis, API, worker, Streamlit):
     ```cmd
     docker-compose up --build
     ```
   - This builds the Docker image, starts Redis on port 6379, Flask API on port 5000, Streamlit on port 8501, and the worker.

3. **Access the Application**:
   - **Streamlit App**: Open `http://localhost:8501` in your browser.
   - **Flask API**: Test endpoints at `http://localhost:5000` (optional, for debugging).
   - **Worker Logs**: View in the terminal running `docker-compose` or via Streamlit's "Worker Logs" section.

4. **Stop the Application**:
   - Press `Ctrl+C` in the Command Prompt to stop the services.
   - Remove containers:
     ```cmd
     docker-compose down
     ```

### Option 2: Run Locally (Without Docker)

1. **Create Project Directory**:
   - Create a folder at `C:\job_queue_system`.
   - Place `api.py`, `worker.py`, `app.py`, and `requirements.txt` in this directory.

2. **Install Python Dependencies**:
   - Open Command Prompt.
   - Navigate to the project directory:
     ```cmd
     cd C:\job_queue_system
     ```
   - Install dependencies:
     ```cmd
     pip install -r requirements.txt
     ```

3. **Start Redis**:
   - Use Docker:
     ```cmd
     docker run -d -p 6379:6379 --name redis redis
     ```
   - Or start Memurai (refer to Memurai documentation).
   - Verify:
     ```cmd
     redis-cli -h localhost -p 6379 ping
     ```
     Expected output: `PONG`

4. **Start the Flask API**:
   - Open a Command Prompt.
   - Navigate to the project directory:
     ```cmd
     cd C:\job_queue_system
     ```
   - Run:
     ```cmd
     python api.py
     ```
     Output: `* Running on http://127.0.0.1:5000`

5. **Start the Worker**:
   - Open a new Command Prompt.
   - Navigate to the project directory:
     ```cmd
     cd C:\job_queue_system
     ```
   - Run:
     ```cmd
     python worker.py
     ```
     Output: `Starting worker... No jobs in queue, waiting...`

6. **Start the Streamlit App**:
   - Open another Command Prompt.
   - Navigate to the project directory:
     ```cmd
     cd C:\job_queue_system
     ```
   - Run:
     ```cmd
     streamlit run app.py
     ```
     Browser opens at `http://localhost:8501`.

## Testing the Application

Use the Streamlit app at `http://localhost:8501` to test the job queue system.

1. **Submit a Job**:
   - In the Streamlit app, go to "Submit a New Job".
   - Fill in:
     - **Job Type**: `send_email` (fixed).
     - **Priority**: `high` or `low`.
     - **To Email**: `user@example.com`.
     - **Subject**: `Test`.
     - **Message**: `Hello!`.
   - Click **Submit Job**.
   - Success: `Job submitted successfully! Job ID: <uuid>` (e.g., `123e4567-e89b-12d3-a456-426614174000`).
   - Error: Displays if fields are missing or invalid.

2. **Check Job Status**:
   - In "Check Job Status", enter the Job ID (auto-filled if recent).
   - Click **Check Status**.
   - View JSON response, e.g.:
     ```json
     {
       "job_type": "send_email",
       "priority": "high",
       "payload": {"to": "user@example.com", "subject": "Test", "message": "Hello!"},
       "status": "completed",
       "created_at": "2025-05-31T22:46:00.123456",
       "picked_at": "2025-05-31T22:46:01.123456",
       "completed_at": "2025-05-31T22:46:03.123456",
       "attempts": 1,
       "max_attempts": 3
     }
     ```

3. **Test Prioritization**:
   - Submit two jobs:
     - First: Priority `low`, Subject `Low Priority`, Message `Low priority test`.
     - Second: Priority `high`, Subject `High Priority`, Message `High priority test`.
   - Check the worker logs (Docker terminal or Streamlit "Worker Logs") to confirm high-priority job processes first:
     ```
     Picked job <high_priority_job_id>
     Processing job <high_priority_job_id>: {'to': 'user@example.com', 'subject': 'High Priority', 'message': 'High priority test'}
     Job <high_priority_job_id> completed successfully
     Picked job <low_priority_job_id>
     ```

4. **Test Retries**:
   - Worker simulates failures (30% chance).
   - Submit a job and check worker logs for retries:
     ```
     Job <job_id> failed: Mock email sending failed
     Retrying job <job_id> after 2 seconds (attempt 1)
     ```
   - After 3 failures:
     ```
     Job <job_id> permanently failed after 3 attempts
     ```

5. **View Worker Logs**:
   - In Streamlit, check "Show Live Worker Logs" to see simulated Redis logs.
   - Example:
     ```
     [2025-05-31 22:46:00] Job 123e4567-e89b-12d3-a456-426614174000:
       Status: completed
       Attempts: 1/3
       Payload: {'to': 'user@example.com', 'subject': 'Test', 'message': 'Hello!'}
       Created At: 2025-05-31T22:46:00.123456
       Picked At: 2025-05-31T22:46:01.123456
       Completed At: 2025-05-31T22:46:03.123456
     ---
     ```
   - For Docker, view logs in the terminal running `docker-compose up`.

## Alternative Testing with curl (Optional)

For non-Streamlit testing:
1. **Submit a Job**:
   ```cmd
   curl -X POST http://localhost:5000/submit-job -H "Content-Type: application/json" -d "{\"job_type\": \"send_email\", \"priority\": \"high\", \"payload\": {\"to\": \"user@example.com\", \"subject\": \"Test\", \"message\": \"Hello!\"}}"

   Response:
{"job_id": "123e4567-e89b-12d3-a456-426614174000", "status": "queued"}


Check Job Status:curl http://localhost:5000/jobs/status/123e4567-e89b-12d3-a456-426614174000



Notes

Prioritization: High-priority jobs (score=1) process before low-priority (score=2).
Retries: Up to 3 attempts with 2^n seconds backoff.
Timestamps: Tracks job lifecycle stages.
No Off-the-Shelf Queues: Uses Redis directly.
Docker Benefits: Simplifies setup, ensures consistency across systems.


## Demo
https://github.com/user-attachments/assets/90697c0e-fb4a-4e1b-9529-93f23876c70d

## Screenshot
![image](https://github.com/user-attachments/assets/c346754a-2e68-458c-969b-b8d640d34013)
![image](https://github.com/user-attachments/assets/1022af37-58b5-4e67-a693-335594cdef1e)
![image](https://github.com/user-attachments/assets/834d7556-57d6-4c78-a97b-8afa9494c25b)

