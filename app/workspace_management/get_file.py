from app import minio_client

from fastapi import APIRouter, HTTPException, Request
import chardet

router = APIRouter()

@router.get("/get_file", status_code=200)
async def get_file(bucket: str, file_path: str):
    try:
        # Use MinIO client to get object. Ensure 'bucket' and 'file' are properly validated and sanitized
        result = minio_client.get_object(bucket_name=bucket, object_name=file_path)
        
        # Get the contents of the response as bytes
        contents = result.data

        # Determine the character encoding
        encoding = chardet.detect(contents)['encoding']

        # Decode the content using the detected encoding
        if encoding is not None:
            try:
                decoded_contents = contents.decode(encoding)
            except UnicodeDecodeError:
                print("Error decoding using detected encoding. Falling back to 'utf-8'.")
                decoded_contents = contents.decode('utf-8', errors='replace')
        else:
            # If encoding is not detected, fallback to UTF-8
            print("Encoding not detected. Falling back to 'utf-8'.")
            decoded_contents = contents.decode('utf-8', errors='replace')

        # Return the file contents
        return {"message": "File retrieved successfully", "result": decoded_contents.splitlines()}
    except Exception as e:
        # You can refine exception handling based on the errors you expect (e.g., file not found, permission issues)
        raise HTTPException(status_code=404, detail=str(e))