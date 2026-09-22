import logging

logger = logging.getLogger(__name__)

def data_executor(job):
    logger.info("Executing data task...")
    return {"job_id": job.get("id"), "type": "data", "status": "completed"}

