import logging
from datetime import datetime

logger = logging.getLogger(__name__)

def finance_agent(result):
    logger.info(f"Recording payment for job {result.get('job_id')} at {datetime.now()}")

