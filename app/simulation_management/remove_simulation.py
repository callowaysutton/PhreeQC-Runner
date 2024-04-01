from app import docker_client, queue
from fastapi import APIRouter, HTTPException

router = APIRouter()

@router.delete("/remove_simulation", status_code=200)
async def remove_simulation(simulation_id: str):
    try:
        # Remove the simulation from the queue
        if simulation_id in queue:
            queue.remove(simulation_id)
        
        # Use Docker client to remove container. Ensure 'simulation_id' is properly validated and sanitized
        result = docker_client.remove_container(container=simulation_id, force=True)
        
        return {"message": "Simulation removed successfully", "result": str(result)}
    except Exception as e:
        # You can refine exception handling based on the errors you expect (e.g., container not found, permission issues)
        raise HTTPException(status_code=500, detail=str(e))