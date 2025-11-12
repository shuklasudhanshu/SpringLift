from pydantic import BaseModel, Field
from typing import List, Dict, Optional
import uuid
from datetime import datetime

class ScanRequest(BaseModel):
    project_path: str = Field(..., description="The path to the legacy Java project to be scanned.")
    use_ai: bool = Field(default=True, description="Enable AI-powered analysis using Claude/OpenAI")
    ai_provider: str = Field(default="openai", description="AI provider: 'openai' or 'anthropic'")

class FileAnalysis(BaseModel):
    filename: str
    filepath: str
    issues: List[str] = []
    suggestions: List[str] = []
    transformations: Dict = {}
    java_version_target: str = "21"
    spring_boot_target: str = "3.x"
    ai_analysis: Optional[str] = None

class ProjectAnalysis(BaseModel):
    file_analyses: List[FileAnalysis] = []
    dependency_issues: List[str] = []
    dependency_upgrades: Dict = {}
    build_file_type: Optional[str] = None  # pom.xml, build.gradle, etc.
    build_recommendations: List[str] = []
    total_files_analyzed: int = 0
    issues_found: int = 0
    total_transformations: int = 0

class ScanResult(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), description="Unique ID for the scan result.")
    request: ScanRequest
    output_path: str = Field(..., description="The path to the modernized project.")
    project_analysis: ProjectAnalysis = Field(default_factory=ProjectAnalysis)
    created_at: datetime = Field(default_factory=datetime.now)
    status: str = Field(default="completed", description="Status: pending, in_progress, completed, failed")
    error_message: Optional[str] = None
