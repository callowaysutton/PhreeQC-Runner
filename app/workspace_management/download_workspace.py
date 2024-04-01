from app import config, minio_client
from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from minio.error import S3Error
from datetime import datetime
import io, zipfile

router = APIRouter()

# Returns a .zip blob containing the workspace files
@router.get("/download_workspace", response_class=StreamingResponse)
async def download_workspace(bucket: str):
    # In-memory bytes buffer for the ZIP file
    in_memory_zip = io.BytesIO()

    # Create a ZIP file in memory
    with zipfile.ZipFile(in_memory_zip, mode="w", compression=zipfile.ZIP_DEFLATED) as zf:
        try:
            # List all objects in the specified workspace within the bucket
            objects = minio_client.list_objects(bucket_name=bucket, recursive=True)
            for obj in objects:
                obj_data = minio_client.get_object(bucket_name=bucket, object_name=obj.object_name)
                # Write file data to the ZIP file
                zf.writestr(obj.object_name, obj_data.read())
        except S3Error as e:
            raise HTTPException(status_code=412, detail=f"Failed to download workspace: {e}")

    # Go to the beginning of the BytesIO buffer
    in_memory_zip.seek(0)

    # Stream the ZIP file
    datetime_now = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    return StreamingResponse(in_memory_zip, media_type="application/zip", headers={"Content-Disposition": f"attachment; filename={bucket}-{datetime_now}.zip"})