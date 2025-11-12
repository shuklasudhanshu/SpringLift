from fastapi import FastAPI, Body, HTTPException
from fastapi.responses import JSONResponse
from .models import ScanRequest, ScanResult, ProjectAnalysis
from .services import genai_service
from .storage import save_scan_result, get_scan_result
from .exceptions import ScanNotFoundException
from .logger import logger
from .validator import InputValidator, validate_request
from .batch_processor import batch_processor
import os

app = FastAPI(
    title="SpringLift",
    description="A GenAI-powered tool to help modernize legacy Java applications. Scans Java 8/11 with Spring Boot 2.x and upgrades to Java 21 with Spring Boot 3.x.",
    version="2.0.0"
)

@app.post("/scan", response_model=ScanResult)
async def scan_code(request: ScanRequest = Body(...)):
    """
    Scans a legacy Java project and returns detailed modernization analysis.
    
    Request body:
    - project_path: Absolute path to the legacy Java project
    - use_ai: Enable AI-powered analysis (requires OPENAI_API_KEY or ANTHROPIC_API_KEY env var)
    - ai_provider: 'openai' or 'anthropic'
    
    Returns a ScanResult with:
    - Detailed file-by-file analysis
    - Dependency upgrade recommendations
    - Path to modernized project
    """
    logger.info(f"Received scan request for project_path: {request.project_path}")
    
    # Validate input
    is_valid, error_msg = validate_request(request)
    if not is_valid:
        logger.error(f"Validation failed: {error_msg}")
        raise HTTPException(status_code=400, detail=error_msg)
    
    result = genai_service.analyze_code(request)
    save_scan_result(result)
    logger.info(f"Scan complete. Result ID: {result.id}")
    return result

@app.get("/scan/{scan_id}", response_model=ScanResult)
async def get_scan(scan_id: str):
    """
    Retrieves a previously completed scan result by its ID.
    
    Returns the full ScanResult with all analysis details.
    """
    logger.info(f"Retrieving scan result for ID: {scan_id}")
    result = get_scan_result(scan_id)
    if not result:
        logger.error(f"Scan with ID '{scan_id}' not found.")
        raise ScanNotFoundException(scan_id)
    logger.info(f"Scan result for ID '{scan_id}' found.")
    return result

@app.post("/scan/async/{scan_id}")
async def get_async_scan_status(scan_id: str):
    """
    Get the status of an asynchronous scan (for future implementation).
    """
    result = get_scan_result(scan_id)
    if not result:
        raise ScanNotFoundException(scan_id)
    return {"scan_id": scan_id, "status": result.status, "created_at": result.created_at}

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "SpringLift",
        "version": "2.0.0"
    }

@app.get("/")
async def root():
    """Welcome endpoint with API information"""
    return {
        "message": "Welcome to SpringLift!",
        "description": "A GenAI-powered tool to modernize legacy Java applications from Java 8/11 + Spring Boot 2.x to Java 21 + Spring Boot 3.x",
        "docs_url": "/docs",
        "version": "2.0.0",
        "features": [
            "Scan legacy Java projects",
            "AI-powered modernization analysis (OpenAI/Anthropic)",
            "Automatic code transformation",
            "Dependency upgrade recommendations",
            "Build file analysis (Maven/Gradle)",
            "Configuration file analysis",
            "Detailed diff reports",
            "HTML report generation",
            "Batch processing support"
        ]
    }

@app.post("/batch/add")
async def add_to_batch(project_paths: dict = Body(...)):
    """
    Add projects to batch processing queue
    
    Request body:
    - projects: List of absolute paths to Java projects
    - use_ai: Enable AI analysis (optional, default: true)
    - ai_provider: AI provider (optional, default: "openai")
    """
    
    projects = project_paths.get("projects", [])
    use_ai = project_paths.get("use_ai", True)
    ai_provider = project_paths.get("ai_provider", "openai")
    
    if not projects:
        raise HTTPException(status_code=400, detail="No projects provided")
    
    if not isinstance(projects, list):
        raise HTTPException(status_code=400, detail="projects must be a list")
    
    added = batch_processor.add_projects_from_list(projects, use_ai, ai_provider)
    
    return {
        "message": f"Added {added} projects to batch queue",
        "queue_size": len(batch_processor.projects),
        "projects_added": added
    }

@app.post("/batch/process")
async def process_batch():
    """
    Process all projects in the batch queue
    """
    
    if not batch_processor.projects:
        raise HTTPException(status_code=400, detail="Batch queue is empty")
    
    report = batch_processor.process_batch()
    
    return {
        "message": "Batch processing completed",
        "report": report
    }

@app.get("/batch/status")
async def batch_status():
    """
    Get status of batch processing
    """
    
    return {
        "batch_id": batch_processor.batch_id,
        "status": "processing" if batch_processor.projects else "idle",
        "queue_size": len(batch_processor.projects),
        "processed": len(batch_processor.results),
        "summary": batch_processor.get_batch_summary()
    }

@app.post("/batch/clear")
async def clear_batch():
    """
    Clear batch queue
    """
    
    queue_size = len(batch_processor.projects)
    batch_processor.clear()
    
    return {
        "message": f"Cleared {queue_size} projects from batch queue",
        "queue_size": 0
    }
