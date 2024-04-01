from app import config, queue, docker_client, logger

from fastapi import APIRouter, WebSocket, HTTPException
import asyncio, threading

router = APIRouter()

@router.get("/get_status")
async def get_status(id: str):
    try:
        container = docker_client.containers.get(id)
        status = container.status
        logs = container.logs().decode('utf-8')
        created_at = container.attrs['Created']
        started_at = container.attrs['State']['StartedAt']
        queue_position = queue.index(id) if id in queue else None
    except:
        logger.warning(f"Container {id} not found")
        raise HTTPException(
            status_code=412,
            detail={
                "message": f"Container {id} not found",
            }
        )
    return {"status": status, "logs": logs, "created_at": created_at, "started_at": started_at, "queue_position": queue_position}

@router.websocket("/ws/logs/{container_id}")
async def stream_docker_logs_to_websocket(websocket: WebSocket, container_id: str):
    await websocket.accept()

    # Get the current event loop
    loop = asyncio.get_running_loop()

    # Function to stream logs in a separate thread
    def stream_logs(event_loop):
        container = docker_client.containers.get(container_id)
        try:
            for log_line in container.logs(stream=True, follow=True):
                log_text = log_line.decode('utf-8').strip()
                # Use the passed event loop to schedule sending logs
                asyncio.run_coroutine_threadsafe(
                    websocket.send_text(log_text), event_loop
                )
        except Exception as e:
            logger.error(f"Error streaming logs: {e}")

    # Start the log streaming in a background thread, pass the event loop
    thread = threading.Thread(target=stream_logs, args=(loop,), daemon=True)
    thread.start()

    try:
        # Keep the connection open
        while True:
            await websocket.receive_text()
    except Exception as e:
        # This will catch when the client disconnects and break the loop
        logger.info(f"WebSocket disconnected: {e}")