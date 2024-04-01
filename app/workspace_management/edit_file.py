from app import config, minio_client
from fastapi import APIRouter, HTTPException, Request

import io

router = APIRouter()

@router.put("/edit_workspace", status_code=200)
async def edit_file(request: Request, bucket: str, file_path: str):
    # Retrieve the request body as text
    file_contents = await request.body()
    file_contents = file_contents.decode('utf-8')  # Decode bytes to string
    # Convert the file contents to BinaryIO object
    file_contents = io.BytesIO(file_contents.encode('utf-8'))
    
    try:
        # Use MinIO client to write file. Ensure 'bucket' and 'file_path' are properly validated and sanitized
        found = minio_client.bucket_exists(bucket)
        if not found:
            raise HTTPException(status_code=404, detail=f"Bucket '{bucket}' not found")
        
        # Writing or overwriting the file at 'file_path' within 'bucket' with 'file_contents'
        result = minio_client.put_object(bucket_name=bucket, object_name=file_path, data=file_contents, length=len(file_contents.getvalue()), content_type='text/plain')
        
        return {"message": "File edited successfully", "result": str(result.last_modified)}
    except Exception as e:
        # You can refine exception handling based on the errors you expect (e.g., bucket not found, permission issues)
        raise HTTPException(status_code=500, detail=str(e))