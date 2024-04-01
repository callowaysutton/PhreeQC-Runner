from app import minio_client
from fastapi import APIRouter, HTTPException, Request

router = APIRouter()

@router.delete("/delete_workspace", status_code=200)
async def delete_workspace(bucket: str, force: bool = False):
    try:
        # Use MinIO client to remove bucket. Ensure 'bucket' is properly validated and sanitized
        found = minio_client.bucket_exists(bucket)
        if not found:
            raise HTTPException(status_code=404, detail=f"Bucket '{bucket}' not found")
        
        if force:
            # List all objects in the specified workspace within the bucket
            objects = minio_client.list_objects(bucket_name=bucket, recursive=True)
            for obj in objects:
                # Remove the object
                minio_client.remove_object(bucket_name=bucket, object_name=obj.object_name)

        # Remove the bucket
        result = minio_client.remove_bucket(bucket_name=bucket)
        
        return {"message": "Workspace deleted successfully", "result": str(result)}
    except Exception as e:
        # You can refine exception handling based on the errors you expect (e.g., bucket not found, permission issues)
        raise HTTPException(status_code=500, detail=str(e))