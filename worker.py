import redis
import json
import time
from datetime import datetime
import random

r = redis.Redis(host='localhost', port=6379, db=0)

def process_job(job_id):
    """
    Process a job by simulating email sending.
    Implements retry logic with exponential backoff.
    """
    # Fetch job data
    job_data = r.hgetall(f'job:{job_id}')
    if not job_data:
        print(f"Job {job_id} not found")
        return
    
    # Decode Redis bytes
    job_data = {k.decode(): v.decode() if isinstance(v, bytes) else v for k, v in job_data.items()}
    
    attempts = int(job_data.get('attempts', 0))
    max_attempts = int(job_data.get('max_attempts', 3))
    
    if attempts >= max_attempts:
        print(f"Job {job_id} has reached max attempts")
        r.hset(f'job:{job_id}', mapping={'status': 'failed', 'failed_at': datetime.utcnow().isoformat()})
        return
    
    # Update status and attempts
    r.hset(f'job:{job_id}', mapping={
        'status': 'processing',
        'picked_at': datetime.utcnow().isoformat(),
        'attempts': attempts + 1
    })
    
    try:
        # Mock email sending
        payload = json.loads(job_data['payload'])
        print(f"Processing job {job_id}: {payload}")
        time.sleep(2)  # Simulate work
        
        # Simulate random failure for testing retries (30% chance)
        if random.random() < 0.3:
            raise Exception("Mock email sending failed")
        
        # Success
        print(f"Job {job_id} completed successfully")
        r.hset(f'job:{job_id}', mapping={
            'status': 'completed',
            'completed_at': datetime.utcnow().isoformat()
        })
    
    except Exception as e:
        print(f"Job {job_id} failed: {str(e)}")
        if attempts + 1 < max_attempts:
            # Calculate exponential backoff (2^attempts seconds)
            backoff = 2 ** attempts
            print(f"Retrying job {job_id} after {backoff} seconds (attempt {attempts + 1})")
            time.sleep(backoff)
            # Re-queue job for retry
            r.zadd('job_queue', {job_id: float(job_data['priority'].replace('high', '1').replace('low', '2'))})
        else:
            print(f"Job {job_id} permanently failed after {max_attempts} attempts")
            r.hset(f'job:{job_id}', mapping={
                'status': 'failed',
                'failed_at': datetime.utcnow().isoformat()
            })

def worker():
    """
    Worker process that polls the job queue and processes jobs.
    """
    print("Starting worker...")
    while True:
        # Poll the queue for the highest-priority job (lowest score)
        job = r.zrange('job_queue', 0, 0)
        if not job:
            print("No jobs in queue, waiting...")
            time.sleep(1)
            continue
        
        job_id = job[0].decode()
        # Remove job from queue atomically
        r.zrem('job_queue', job_id)
        print(f"Picked job {job_id}")
        process_job(job_id)

if __name__ == '__main__':
    worker()