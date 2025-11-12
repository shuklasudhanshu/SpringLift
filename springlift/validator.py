"""
Input Validation Module
Validates and sanitizes user inputs for security and reliability
"""
import os
import re
from pathlib import Path
from typing import Tuple
from .logger import logger


class InputValidator:
    """
    Validates user inputs for security and correctness
    """
    
    # Maximum path length
    MAX_PATH_LENGTH = 4096
    
    # Dangerous path patterns
    DANGEROUS_PATTERNS = [
        r'\.\.',           # Parent directory traversal
        r'\0',             # Null bytes
        r'[\x00-\x1f]',    # Control characters
    ]
    
    @staticmethod
    def validate_project_path(project_path: str) -> Tuple[bool, str]:
        """
        Validates a project path for:
        - Existence
        - Accessibility
        - Path traversal attacks
        - Symlink attacks
        - Sufficient permissions
        
        Returns: (is_valid, error_message)
        """
        
        # 1. Check for empty/None
        if not project_path or not isinstance(project_path, str):
            return False, "Project path cannot be empty or null"
        
        # 2. Check length
        if len(project_path) > InputValidator.MAX_PATH_LENGTH:
            return False, f"Project path exceeds maximum length of {InputValidator.MAX_PATH_LENGTH} characters"
        
        # 3. Check for dangerous patterns
        for pattern in InputValidator.DANGEROUS_PATTERNS:
            if re.search(pattern, project_path):
                return False, f"Project path contains invalid characters or patterns: {pattern}"
        
        # 4. Normalize and check for path traversal
        try:
            normalized = os.path.normpath(project_path)
            # Ensure path is absolute
            if not os.path.isabs(normalized):
                return False, "Project path must be an absolute path (e.g., /home/user/project or C:\\Users\\project)"
        except (ValueError, OSError) as e:
            return False, f"Invalid path format: {str(e)}"
        
        # 5. Check if path exists
        if not os.path.exists(normalized):
            return False, f"Project path does not exist: {normalized}"
        
        # 6. Check if it's a directory
        if not os.path.isdir(normalized):
            return False, f"Project path is not a directory: {normalized}"
        
        # 7. Check for symlink (security risk)
        if os.path.islink(normalized):
            logger.warning(f"Project path is a symlink: {normalized}")
            # Note: We allow symlinks but log warning
        
        # 8. Check read permissions
        if not os.access(normalized, os.R_OK):
            return False, f"No read permission for project path: {normalized}"
        
        # 9. Check for Java files (must have at least one)
        java_files = InputValidator._find_java_files(normalized)
        if not java_files:
            logger.warning(f"No Java files found in project path: {normalized}")
            # Note: We allow this but log warning
        
        return True, ""
    
    @staticmethod
    def validate_ai_provider(provider: str) -> Tuple[bool, str]:
        """
        Validates AI provider name
        
        Returns: (is_valid, error_message)
        """
        
        if not provider or not isinstance(provider, str):
            return False, "AI provider cannot be empty"
        
        provider = provider.lower().strip()
        
        valid_providers = ["openai", "anthropic"]
        
        if provider not in valid_providers:
            return False, f"Invalid AI provider '{provider}'. Must be one of: {', '.join(valid_providers)}"
        
        return True, ""
    
    @staticmethod
    def validate_scan_id(scan_id: str) -> Tuple[bool, str]:
        """
        Validates scan ID format (UUID)
        
        Returns: (is_valid, error_message)
        """
        
        if not scan_id or not isinstance(scan_id, str):
            return False, "Scan ID cannot be empty"
        
        # UUID format: xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
        uuid_pattern = r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$'
        
        if not re.match(uuid_pattern, scan_id.lower()):
            return False, f"Invalid scan ID format: {scan_id}"
        
        return True, ""
    
    @staticmethod
    def sanitize_filename(filename: str) -> str:
        """
        Sanitizes a filename by removing dangerous characters
        
        Returns: sanitized filename
        """
        
        # Remove or replace dangerous characters
        filename = re.sub(r'[<>:"/\\|?*]', '_', filename)
        filename = re.sub(r'[\x00-\x1f]', '', filename)
        filename = re.sub(r'\.{2,}', '_', filename)  # Replace multiple dots
        
        # Remove leading/trailing spaces and dots
        filename = filename.strip(' .')
        
        # Ensure it's not empty
        if not filename:
            filename = "sanitized_file"
        
        # Limit length
        if len(filename) > 255:
            filename = filename[:255]
        
        return filename
    
    @staticmethod
    def validate_output_path(base_path: str, output_path: str) -> Tuple[bool, str]:
        """
        Validates that output path is within allowed directory
        
        Returns: (is_valid, error_message)
        """
        
        if not output_path:
            return False, "Output path cannot be empty"
        
        try:
            base_normalized = os.path.normpath(os.path.abspath(base_path))
            output_normalized = os.path.normpath(os.path.abspath(output_path))
            
            # Ensure output is within base (prevent directory traversal)
            if not output_normalized.startswith(base_normalized.rstrip(os.sep) + os.sep):
                # Also allow if output equals base directory
                if output_normalized != base_normalized:
                    return False, "Output path must be within project directory"
        except (ValueError, OSError) as e:
            return False, f"Invalid output path: {str(e)}"
        
        return True, ""
    
    @staticmethod
    def _find_java_files(directory: str) -> list:
        """
        Find all Java files in directory
        
        Returns: list of .java file paths
        """
        java_files = []
        
        try:
            for root, dirs, files in os.walk(directory):
                # Skip hidden directories and common exclusions
                dirs[:] = [d for d in dirs if not d.startswith('.') and d not in ['__pycache__', 'node_modules']]
                
                for file in files:
                    if file.endswith('.java'):
                        java_files.append(os.path.join(root, file))
        except (OSError, PermissionError) as e:
            logger.warning(f"Could not search directory {directory}: {str(e)}")
        
        return java_files


# Request validation decorator
def validate_request(request):
    """
    Validates incoming request
    """
    validator = InputValidator()
    
    # Validate project path
    is_valid, error = validator.validate_project_path(request.project_path)
    if not is_valid:
        return False, f"Invalid project_path: {error}"
    
    # Validate AI provider if use_ai is True
    if request.use_ai:
        is_valid, error = validator.validate_ai_provider(request.ai_provider)
        if not is_valid:
            return False, f"Invalid ai_provider: {error}"
    
    return True, ""
