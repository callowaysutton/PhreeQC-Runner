from app import docker_client, config, queue, global_checksums, logger
from app.simulation_management.checksumming import calculate_checksum

from fastapi import APIRouter, HTTPException
import os, time

router = APIRouter()

@router.post("/run_simulation")
async def run_simulation(s3_bucket: str, command: str, output_file: str = "", database_file: str = "", input_file: str = "", bypass_checksum: bool = True):
    # --- Check to see if the input, output and database files are passed. ---
    if input_file and output_file and database_file:
        command = f"phreeqc /data/{input_file} /data/{output_file} /data/{database_file}"
        bypass_checksum = False
    elif not command:
        raise HTTPException(
            status_code=412,
            detail={
                "message": "No command provided",
                "solution": "Please provide a command or input, output and database files."
            }
        )

    # --- Loading the input files from the S3 bucket stage. ---
    try:
        os.system(f'umount /tmp/{s3_bucket}')
        os.system(f'rm -rf /tmp/{s3_bucket}')
        os.system(f'mkdir /tmp/{s3_bucket}')
        os.system(f"s3fs {s3_bucket} /tmp/{s3_bucket} -o url=http://{config['minio_URL']} -o use_path_request_style -o allow_other -o nonempty -o passwd_file=/etc/.s3fs_passwd")
    except:
        print("LOG [ERROR]: Could not mount S3 bucket, maybe already mounted?")
        print('Bucket Contents: ', os.listdir(f'/tmp/{s3_bucket}'))
    
    # --- Checksumming the input files to deduplicate runs. ---
    if not bypass_checksum and input_file and database_file:
        # Only calculate the checksums of .pqi and .dat files
        checksum = ""
        checksum += calculate_checksum(f'/tmp/{s3_bucket}/{input_file}')
        checksum += calculate_checksum(f'/tmp/{s3_bucket}/{database_file}')
        if checksum in global_checksums:
            return {"message": "Simulation already run with the same input and database files.", "checksum": checksum, "container_id": None}
        else:
            global_checksums.append(checksum)
    
    # --- Running a test simulation with the given command. ---
    container = docker_client.containers.run(
        image="callowaysutton/phreeqc",
        command=f"{command}",
        volumes=[f'/tmp/{s3_bucket}:/data:rshared'],
        privileged=True,
        detach=True,
    )
    time.sleep(0.05)
    logs = container.logs().decode('utf-8')
    try:
        container.kill(signal='SIGKILL')
    except:
        print("LOG [INFO]: Could not kill container, maybe already killed?")
    container.wait()
    container.remove(force=True)
    if logs.find("ERROR") != -1:
        # Return a 400 error if the logs contain the word "ERROR"
        raise HTTPException(
            status_code=412,
            detail={
                "message": f"Error running simulation with command: {command}",
                "solution": "Please check file paths used and/or input files.",
                "logs": logs
            }
        )
    
    # --- Adding the simulation to the queue. ---
    
    # Create the host configuration with the necessary settings, including the privileged flag
    host_config = docker_client.api.create_host_config(
        binds=[f'/tmp/{s3_bucket}:/data:rshared'],
        privileged=True
    )

    # Create the container with the host configuration
    container = docker_client.api.create_container(
        image="callowaysutton/phreeqc",
        command=f"{command}",
        host_config=host_config
    )
    
    logger.info(f"Adding {container.get('Id')} to the queue")
    # Add the container to the queue
    queue.append(container.get('Id'))
    return {"message": f"Adding simulation to the queue with command: {command}", "container_id": container.get('Id'), "queue_length": len(queue), "queue_position": queue.index(container.get('Id'))}