import streamlit as st
import requests
import json
import time
import redis
from datetime import datetime

# Streamlit app configuration
st.set_page_config(page_title="Job Queue Tester", page_icon="🚀", layout="wide")

# Initialize Redis connection
r = redis.Redis(host='localhost', port=6379, db=0)

# Flask API base URL
API_BASE_URL = "http://localhost:5000"

def submit_job(job_type, priority, to_email, subject, message):
    """
    Submit a job to the Flask API.
    """
    payload = {
        "job_type": job_type,
        "priority": priority,
        "payload": {
            "to": to_email,
            "subject": subject,
            "message": message
        }
    }
    try:
        response = requests.post(f"{API_BASE_URL}/submit-job", json=payload)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        return {"error": f"Failed to submit job: {str(e)}"}

def get_job_status(job_id):
    """
    Fetch job status from the Flask API.
    """
    try:
        response = requests.get(f"{API_BASE_URL}/jobs/status/{job_id}")
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        return {"error": f"Failed to fetch job status: {str(e)}"}

def fetch_worker_logs():
    """
    Fetch job data from Redis to simulate worker logs.
    """
    jobs = r.keys("job:*")
    log_output = []
    for job_key in jobs:
        job_data = r.hgetall(job_key)
        job_data = {k.decode(): v.decode() if isinstance(v, bytes) else v for k, v in job_data.items()}
        job_id = job_key.decode().replace("job:", "")
        log_output.append(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Job {job_id}:")
        log_output.append(f"  Status: {job_data.get('status', 'unknown')}")
        log_output.append(f"  Attempts: {job_data.get('attempts', '0')}/{job_data.get('max_attempts', '3')}")
        if "payload" in job_data:
            payload = json.loads(job_data["payload"])
            log_output.append(f"  Payload: {payload}")
        for key in ["created_at", "picked_at", "completed_at", "failed_at"]:
            if key in job_data:
                log_output.append(f"  {key.replace('_', ' ').title()}: {job_data[key]}")
        log_output.append("---")
    return "\n".join(log_output)

# Streamlit UI
st.title("Job Queue System Tester")

# Section 1: Submit a Job
st.header("Submit a New Job")
with st.form("submit_job_form"):
    job_type = st.selectbox("Job Type", ["send_email"], disabled=True)  # Only send_email supported
    priority = st.selectbox("Priority", ["high", "low"])
    to_email = st.text_input("To Email", value="user@example.com")
    subject = st.text_input("Subject", value="Test")
    message = st.text_area("Message", value="Hello!")
    submit_button = st.form_submit_button("Submit Job")

    if submit_button:
        if not to_email or not subject or not message:
            st.error("Please fill in all fields.")
        else:
            result = submit_job(job_type, priority, to_email, subject, message)
            if "error" in result:
                st.error(result["error"])
            else:
                st.success(f"Job submitted successfully! Job ID: {result['job_id']}")
                st.session_state["last_job_id"] = result["job_id"]

# Section 2: Check Job Status
st.header("Check Job Status")
job_id_input = st.text_input("Job ID", value=st.session_state.get("last_job_id", ""))
if st.button("Check Status"):
    if not job_id_input:
        st.error("Please enter a Job ID.")
    else:
        status = get_job_status(job_id_input)
        if "error" in status:
            st.error(status["error"])
        else:
            st.json(status)

# Section 3: Worker Logs
st.header("Worker Logs")
st.write("Simulated worker logs (for real-time logs, check worker.py terminal).")
log_placeholder = st.empty()

# Use a single checkbox with a unique key
show_logs = st.checkbox("Show Live Worker Logs", key="show_logs_checkbox")

if show_logs:
    while True:
        log_placeholder.text(fetch_worker_logs())
        time.sleep(2)  # Update every 2 seconds
        # Check if checkbox is still enabled to allow stopping the loop
        if not st.session_state.get("show_logs_checkbox", False):
            break

# Instructions
st.sidebar.header("Instructions")
st.sidebar.markdown("""
1. Ensure Redis is running (`docker run -d -p 6379:6379 redis` or Memurai).
2. Start the Flask API (`python api.py`).
3. Start the worker (`python worker.py`) in a separate terminal.
4. Use the form to submit jobs and check their status.
5. Monitor worker logs in the 'Worker Logs' section or in the worker terminal.
""")