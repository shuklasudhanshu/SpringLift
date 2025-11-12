from fastapi.testclient import TestClient
from springlift.main import app
from springlift.storage import clear_storage
import pytest
import tempfile
import os
import shutil

client = TestClient(app)

@pytest.fixture(autouse=True)
def run_before_and_after_tests():
    """Fixture to clear storage before and after each test."""
    clear_storage()
    yield
    clear_storage()

def test_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Welcome to SpringLift! Visit /docs for API documentation."}



def test_scan_project():
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create a dummy Java project
        project_path = os.path.join(tmpdir, "my-java-project")
        os.makedirs(os.path.join(project_path, "src", "main", "java", "com", "example"), exist_ok=True)
        
        with open(os.path.join(project_path, "src", "main", "java", "com", "example", "App.java"), "w") as f:
            f.write("package com.example;\n\npublic class App {\n    public static void main(String[] args) {\n        System.out.println(\"Hello World!\");\n    }\n}\n")
        
        with open(os.path.join(project_path, "pom.xml"), "w") as f:
            f.write("<project><modelVersion>4.0.0</modelVersion><groupId>com.example</groupId><artifactId>my-app</artifactId><version>1.0-SNAPSHOT</version></project>")

        request_data = {
            "project_path": project_path
        }
        response = client.post("/scan", json=request_data)
        assert response.status_code == 200
        data = response.json()
        assert "id" in data
        assert data["request"]["project_path"] == project_path
        assert "output_path" in data

        output_path = data["output_path"]
        assert os.path.exists(output_path)
        
        # Verify that the modernized file exists and contains the mock upgrade comment
        modernized_app_java_path = os.path.join(output_path, "src", "main", "java", "com", "example", "App.java")
        assert os.path.exists(modernized_app_java_path)
        with open(modernized_app_java_path, "r") as f:
            content = f.read()
            assert "/**\n * This file has been upgraded by SpringLift.\n */" in content

def test_get_scan_result():
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create a dummy Java project
        project_path = os.path.join(tmpdir, "my-java-project")
        os.makedirs(os.path.join(project_path, "src", "main", "java", "com", "example"), exist_ok=True)
        
        with open(os.path.join(project_path, "src", "main", "java", "com", "example", "App.java"), "w") as f:
            f.write("package com.example;\n\npublic class App {\n    public static void main(String[] args) {\n        System.out.println(\"Hello World!\");\n    }\n}\n")

        # First, create a scan
        request_data = {
            "project_path": project_path
        }
        post_response = client.post("/scan", json=request_data)
        scan_id = post_response.json()["id"]

        # Now, get the result
        get_response = client.get(f"/scan/{scan_id}")
        assert get_response.status_code == 200
        data = get_response.json()
        assert data["id"] == scan_id
        assert data["request"]["project_path"] == project_path
        assert "output_path" in data

def test_get_scan_not_found():
    response = client.get("/scan/non_existent_id")
    assert response.status_code == 404
    assert response.json() == {"detail": "Scan with ID 'non_existent_id' not found."}
