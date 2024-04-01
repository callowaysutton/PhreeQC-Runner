from app import minio_client

from fastapi import APIRouter, HTTPException, Request

router = APIRouter()

@router.put("/create_workspace", status_code=200)
async def create_workspace(bucket: str):
    try:
        # Use MinIO client to create bucket. Ensure 'bucket' is properly validated and sanitized
        found = minio_client.bucket_exists(bucket)
        if found:
            raise HTTPException(status_code=409, detail=f"Bucket '{bucket}' already exists")
        
        # Create the bucket
        result = minio_client.make_bucket(bucket_name=bucket)
        
        return {"message": "Workspace created successfully", "result": str(result)}
    except Exception as e:
        # You can refine exception handling based on the errors you expect (e.g., bucket already exists, permission issues)
        raise HTTPException(status_code=500, detail=str(e))