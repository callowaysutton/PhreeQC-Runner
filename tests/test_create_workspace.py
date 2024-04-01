import sys
from pathlib import Path

# Add the project root directory to sys.path
root_path = Path(__file__).parent.parent  # Adjust as necessary
sys.path.append(str(root_path))

import pytest
from httpx import AsyncClient
from unittest.mock import patch
from app import app

@pytest.mark.asyncio
async def test_create_workspace():
    async with AsyncClient(app=app, base_url="http://test/runner") as ac:
        bucket_name = "testbucket"

        # Scenario 1: Bucket does not exist
        with patch("app.minio_client.bucket_exists", return_value=False) as mock_bucket_exists:
            with patch("app.minio_client.make_bucket", return_value=True) as mock_make_bucket:
                response = await ac.put(f"/create_workspace/?bucket_name={bucket_name}")
                assert response.status_code == 200
                print(response.json())
                assert response.json() == {"message": "Workspace created successfully", "result": "None"}
                mock_bucket_exists.assert_called_once_with(bucket_name)
                mock_make_bucket.assert_called_once_with(bucket_name=bucket_name)

        # Scenario 2: Bucket already exists
        with patch("app.minio_client.bucket_exists", return_value=True):
            response = await ac.put("/create_workspace", json={"bucket": bucket_name})
            assert response.status_code == 409
            assert "already exists" in response.json()["detail"]

        # Scenario 3: Exception handling
        with patch("app.minio_client.bucket_exists", side_effect=Exception("Test error")):
            response = await ac.put("/create_workspace", json={"bucket": bucket_name})
            assert response.status_code == 500
            assert response.json()["detail"] == "Test error"
