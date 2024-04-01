from app import config, minio_client
from fastapi import APIRouter, HTTPException, Form, File, UploadFile

router = APIRouter()

@router.put("/upload_file", status_code=200)
async def upload_file(bucket: str = Form(...), file_path: str = Form(...), file: UploadFile = File(...)):
    # Get the mimetype of the file
    mimetype = file.content_type
    
    try:
        # Use MinIO client to write file. Ensure 'bucket' and 'file_path' are properly validated and sanitized
        found = minio_client.bucket_exists(bucket)
        if not found:
            raise HTTPException(status_code=404, detail=f"Bucket '{bucket}' not found")
        
        # Writing or overwriting the file at 'file_path' within 'bucket' with 'file_contents'
        result = minio_client.put_object(bucket_name=bucket, object_name=file_path, data=file, length=len(file.read()), content_type=mimetype)
        
        return {"message": "File edited successfully", "result": str(result.last_modified)}
    except Exception as e:
        # You can refine exception handling based on the errors you expect (e.g., bucket not found, permission issues)
        raise HTTPException(status_code=500, detail=str(e))