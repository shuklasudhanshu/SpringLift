"""
Batch Processing Module
Allows scanning and processing multiple projects in sequence
"""
import os
from typing import List, Dict, Optional
from datetime import datetime
from .models import ScanRequest, ScanResult
from .services import genai_service
from .storage import save_scan_result
from .logger import logger
import json


class BatchProcessor:
    """
    Processes multiple Java projects in batch mode
    """
    
    def __init__(self):
        self.batch_id = None
        self.projects = []
        self.results = []
        self.start_time = None
        self.end_time = None
    
    def add_project(self, project_path: str, use_ai: bool = True, ai_provider: str = "openai") -> bool:
        """
        Add a project to the batch queue
        
        Returns: True if successfully added
        """
        
        if not os.path.exists(project_path):
            logger.error(f"Project path does not exist: {project_path}")
            return False
        
        if not os.path.isdir(project_path):
            logger.error(f"Path is not a directory: {project_path}")
            return False
        
        project = {
            "path": os.path.abspath(project_path),
            "use_ai": use_ai,
            "ai_provider": ai_provider,
            "status": "pending",
            "result": None
        }
        
        self.projects.append(project)
        logger.info(f"Added project to batch: {project_path}")
        return True
    
    def add_projects_from_list(self, project_paths: List[str], use_ai: bool = True, ai_provider: str = "openai") -> int:
        """
        Add multiple projects from a list
        
        Returns: Number of projects successfully added
        """
        
        added = 0
        
        for path in project_paths:
            if self.add_project(path, use_ai, ai_provider):
                added += 1
        
        logger.info(f"Added {added} projects to batch queue")
        return added
    
    def process_batch(self) -> Dict:
        """
        Process all projects in the batch
        
        Returns: Batch processing report
        """
        
        if not self.projects:
            logger.warning("No projects in batch queue")
            return {"status": "empty", "message": "No projects to process"}
        
        self.start_time = datetime.now()
        successful = 0
        failed = 0
        
        logger.info(f"Starting batch processing of {len(self.projects)} projects")
        
        for idx, project in enumerate(self.projects, 1):
            project_path = project["path"]
            project_name = os.path.basename(project_path)
            
            logger.info(f"[{idx}/{len(self.projects)}] Processing: {project_name}")
            
            try:
                # Create scan request
                request = ScanRequest(
                    project_path=project_path,
                    use_ai=project["use_ai"],
                    ai_provider=project["ai_provider"]
                )
                
                # Analyze code
                result = genai_service.analyze_code(request)
                
                # Save result
                save_scan_result(result)
                
                # Update project status
                project["status"] = "completed"
                project["result"] = result
                self.results.append({
                    "project": project_name,
                    "scan_id": result.id,
                    "output_path": result.output_path,
                    "status": "success"
                })
                
                successful += 1
                logger.info(f"✓ Successfully processed: {project_name}")
            
            except Exception as e:
                project["status"] = "failed"
                project["error"] = str(e)
                self.results.append({
                    "project": project_name,
                    "status": "failed",
                    "error": str(e)
                })
                
                failed += 1
                logger.error(f"✗ Failed to process {project_name}: {str(e)}")
        
        self.end_time = datetime.now()
        duration = (self.end_time - self.start_time).total_seconds()
        
        report = {
            "status": "completed",
            "total_projects": len(self.projects),
            "successful": successful,
            "failed": failed,
            "duration_seconds": round(duration, 2),
            "start_time": self.start_time.isoformat(),
            "end_time": self.end_time.isoformat(),
            "results": self.results
        }
        
        logger.info(f"Batch processing complete: {successful} succeeded, {failed} failed")
        
        return report
    
    def process_batch_async(self, callback=None) -> str:
        """
        Process batch asynchronously with callback
        
        Returns: Batch ID for tracking
        """
        
        import uuid
        self.batch_id = str(uuid.uuid4())
        
        logger.info(f"Starting async batch processing with ID: {self.batch_id}")
        
        # In a real application, this would be done with async/queue system
        # For now, we'll do synchronous processing
        
        report = self.process_batch()
        report["batch_id"] = self.batch_id
        
        if callback:
            callback(report)
        
        return self.batch_id
    
    def get_batch_summary(self) -> Dict:
        """
        Get summary of batch processing results
        """
        
        if not self.results:
            return {"status": "pending", "projects_processed": 0}
        
        successful = sum(1 for r in self.results if r.get("status") == "success")
        failed = sum(1 for r in self.results if r.get("status") == "failed")
        
        return {
            "batch_id": self.batch_id,
            "total_projects": len(self.results),
            "successful": successful,
            "failed": failed,
            "success_rate": round(successful / max(1, len(self.results)) * 100, 2),
            "start_time": self.start_time.isoformat() if self.start_time else None,
            "end_time": self.end_time.isoformat() if self.end_time else None,
            "duration_seconds": (self.end_time - self.start_time).total_seconds() if self.start_time and self.end_time else None
        }
    
    def export_batch_report(self, output_path: str) -> bool:
        """
        Export batch processing report as JSON
        """
        
        try:
            report = {
                "batch_summary": self.get_batch_summary(),
                "results": self.results,
                "projects": self.projects
            }
            
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(report, f, indent=2)
            
            logger.info(f"Batch report exported to {output_path}")
            return True
        
        except Exception as e:
            logger.error(f"Failed to export batch report: {str(e)}")
            return False
    
    def clear(self):
        """Clear batch data for next processing"""
        
        self.batch_id = None
        self.projects = []
        self.results = []
        self.start_time = None
        self.end_time = None
        logger.info("Batch processor cleared")


# Singleton instance
batch_processor = BatchProcessor()
