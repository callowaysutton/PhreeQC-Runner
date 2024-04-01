from app import minio_client

from fastapi import APIRouter, HTTPException, Request

router = APIRouter()

@router.get("/get_workspaces", status_code=200)
async def get_workspaces():
    try:
        # Use MinIO client to list all of the buckets
        buckets = minio_client.list_buckets()
        
        return {"message": "Workspaces retrieved successfully", "result": [bucket.name for bucket in buckets]}
    except Exception as e:
        # You can refine exception handling based on the errors you expect (e.g., permission issues)
        raise HTTPException(status_code=500, detail=str(e))