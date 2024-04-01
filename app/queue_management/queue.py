from app import queue, docker_client, logger
import asyncio, os

async def check_and_manage_queue():
    logger.info("Starting queue management")
    nthreads = os.cpu_count() // 2

    while True:  # Infinite loop to continuously check the queue
        if queue:  # Check if the queue is not empty
            current_containers = queue[0:nthreads]  # Get the front of the queue
            for i, current_container in enumerate(current_containers):
                if docker_client.api.inspect_container(current_container)['State']['Status'] == "created":
                    logger.info(f"Starting {current_container} from the queue")
                    docker_client.api.start(container=current_container)
                # Example condition check (you would replace this with your actual condition, such as a time check)
                if docker_client.api.inspect_container(current_container)['State']['Status'] != "running":  # If some condition is met
                    # Stop the current container
                    logger.info(f"Removing {current_container} from the queue")
                    # Get the simulation's s3fs mount name from the label
                    s3_bucket = docker_client.api.inspect_container(current_container)['Config']['Labels']['s3_bucket']
                    # Remove the simulation's s3fs mount
                    os.system(f'umount /tmp/{s3_bucket}')
                    container = docker_client.containers.get(current_container)
                    container.remove(force=True)
                    queue.pop(i)  # Remove the container from the queue
            await asyncio.sleep(5)  # Wait for 5 seconds before checking the queue again
        else:
            await asyncio.sleep(5)  # Wait for 5 seconds if the queue is empty