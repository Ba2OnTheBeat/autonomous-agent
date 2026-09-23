import time
import logging
from agents.job_hunter.hunter import job_hunter_loop
from agents.task_executor.research_agent import research_executor
from agents.task_executor.seo_agent import seo_executor
from agents.task_executor.data_agent import data_executor
from agents.delivery.delivery_agent import delivery_agent
from agents.delivery.agents.finance.finance_agent import finance_agent

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    logger.info("Starting autonomous agent system...")
    while True:
        try:
            jobs = job_hunter_loop()

            for job in jobs:
                logger.info(f"Processing job: {job.get('id')} (type: {job.get('type')})")

                job_type = job.get('type', 'research').lower()
                result = None

                if job_type == 'research':
                    result = research_executor(job)
                elif job_type == 'seo':
                    result = seo_executor(job)
                elif job_type == 'data':
                    result = data_executor(job)
                else:
                    logger.warning(f"Unknown job type: {job_type}")
                    continue

                if result:
                    delivery_agent(result)
                    finance_agent(result)

            logger.info("Cycle complete, sleeping 10 seconds...")
            time.sleep(10)

        except Exception as e:
            logger.error(f"Error in main loop: {e}", exc_info=True)
            time.sleep(10)

if __name__ == "__main__":
    main()
