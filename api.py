from flask import Flask, request, jsonify
import redis
import uuid
import json
from datetime import datetime

app = Flask(__name__)
r = redis.Redis(host='localhost', port=6379, db=0)

# Priority mapping for sorted set scores
PRIORITY_SCORES = {"high": 1, "low": 2}

@app.route('/submit-job', methods=['POST'])
def submit_job():
    """
    REST endpoint to submit a job to the queue.
    Expects JSON payload with job_type, priority, and payload.
    """
    data = request.get_json()
    
    # Validate job schema
    required_fields = ['job_type', 'priority', 'payload']
    if not all(field in data for field in required_fields):
        return jsonify({"error": "Missing required fields"}), 400
    
    if data['job_type'] != 'send_email':
        return jsonify({"error": "Unsupported job_type"}), 400
    
    if data['priority'] not in PRIORITY_SCORES:
        return jsonify({"error": "Invalid priority"}), 400
    
    # Generate unique job ID
    job_id = str(uuid.uuid4())
    
    # Job metadata
    job_data = {
        'job_type': data['job_type'],
        'priority': data['priority'],
        'payload': json.dumps(data['payload']),  # Store payload as JSON string
        'status': 'queued',
        'created_at': datetime.utcnow().isoformat(),
        'attempts': 0,
        'max_attempts': 3
    }
    
    # Store job metadata in Redis hash
    r.hset(f'job:{job_id}', mapping=job_data)
    
    # Add job to priority queue (sorted set)
    r.zadd('job_queue', {job_id: PRIORITY_SCORES[data['priority']]})
    
    return jsonify({"job_id": job_id, "status": "queued"}), 201

@app.route('/jobs/status/<job_id>', methods=['GET'])
def job_status(job_id):
    """
    REST endpoint to check the status of a job by job_id.
    """
    job_data = r.hgetall(f'job:{job_id}')
    if not job_data:
        return jsonify({"error": "Job not found"}), 404
    
    # Decode Redis bytes and convert to appropriate types
    job_data = {k.decode(): v.decode() if isinstance(v, bytes) else v for k, v in job_data.items()}
    job_data['attempts'] = int(job_data['attempts'])
    job_data['max_attempts'] = int(job_data['max_attempts'])
    job_data['payload'] = json.loads(job_data['payload'])
    return jsonify(job_data), 200

if __name__ == '__main__':
    app.run(debug=True, port=5000)  