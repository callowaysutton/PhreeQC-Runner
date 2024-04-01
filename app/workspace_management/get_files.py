from app import minio_client

from fastapi import APIRouter, HTTPException, Request

router = APIRouter()

@router.get("/get_files", status_code=200)
async def get_files(bucket: str):
    try:
        # Use Minio client to list all of the objects within the specified workspace directory
        objects = minio_client.list_objects(bucket_name=bucket, recursive=True)
        
        return {"message": "Files retrieved successfully", "result": [obj.object_name for obj in objects]}
    except Exception as e:
        # You can refine exception handling based on the errors you expect (e.g., bucket not found, permission issues)
        raise HTTPException(status_code=500, detail=str(e))