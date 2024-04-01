# Initializes a FastAPI project and sets up the database connection.
# This API is a simple REST API that allows users to run PHREEQC simulations using Docker, query the status of the simulations, and retrieve the results of the simulations.
# The API is built using FastAPI, a modern Python web framework that is designed to be fast to code and fast to run.

from fastapi import FastAPI, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from minio import Minio
import os, docker, asyncio, logging

# Setup globals
app = FastAPI()
logger = logging.getLogger("uvicorn")
queue = []
global_checksums = []

# Get configuration details from the .env file
load_dotenv()

config = {}
config['prefix'] = os.getenv("URL_PREFIX") or ""
config['minio_URL'] = os.getenv("MINIO_URL") or ""
config['minio_access_key'] = os.getenv("MINIO_ACCESS_KEY") or ""
config['minio_secret_key'] = os.getenv("MINIO_SECRET") or ""

# Set up connection to Minio
minio_client = Minio(
    endpoint=config['minio_URL'],
    access_key=config['minio_access_key'],
    secret_key=config['minio_secret_key'],
    secure=False  # Set to True if you are using HTTPS
)

with open('/etc/.s3fs_passwd', 'w') as f:
    f.write(f"{config['minio_access_key']}:{config['minio_secret_key']}\n")

os.system('chmod 600 /etc/.s3fs_passwd')

docker_client = docker.from_env()

from app import routes
from app.queue_management.queue import check_and_manage_queue
# Startup tasks
@app.on_event("startup")
async def startup_event():
    # Use a background task to start checking the queue on server startup
    task = asyncio.create_task(check_and_manage_queue())

# Cleanly stop the queue management task on shutdown
@app.on_event("shutdown")
async def shutdown_event():
    if queue:
        logger.warning("Shutting down queue management")
        for container_id in queue:
            logger.info(f"Removing {container_id}")
            try:
                container = docker_client.containers.get(container_id)
                container.remove(force=True)
            except:
                pass
    else:
        logger.info("Queue is empty, shutting down queue management")