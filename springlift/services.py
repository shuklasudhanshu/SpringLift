import os
import shutil
from pathlib import Path
from typing import Optional
from .models import ScanRequest, ScanResult, ProjectAnalysis, FileAnalysis
from .java_modernizer import java_modernizer
from .logger import logger
from .config_analyzer import config_analyzer
from .diff_report import diff_report_generator
from .report_generator import html_report_generator
from .pom_updater import pom_updater
from .gradle_updater import gradle_updater
import json


class LLMService:
    """
    Service for AI-powered code analysis using OpenAI or Anthropic
    """
    
    def __init__(self):
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        self.anthropic_api_key = os.getenv("ANTHROPIC_API_KEY")
        self.use_openai = bool(self.openai_api_key)
        self.use_anthropic = bool(self.anthropic_api_key)

    def analyze_code_with_ai(self, code: str, filename: str, provider: str = "openai") -> Optional[str]:
        """
        Analyzes Java code using LLM for detailed modernization suggestions
        """
        if not code or len(code) < 10:
            return None

        prompt = self._build_analysis_prompt(code, filename)

        try:
            if provider == "openai" and self.use_openai:
                return self._analyze_with_openai(prompt)
            elif provider == "anthropic" and self.use_anthropic:
                return self._analyze_with_anthropic(prompt)
            else:
                logger.warning(f"AI provider {provider} not configured, skipping AI analysis")
                return None
        except Exception as e:
            logger.error(f"AI analysis failed for {filename}: {str(e)}")
            return None

    def _build_analysis_prompt(self, code: str, filename: str) -> str:
        """Build the analysis prompt for LLM"""
        return f"""You are an expert Java developer specializing in modernizing legacy code.

Analyze this Java file ({filename}) and provide specific modernization recommendations for upgrading from Java 8/11 with Spring Boot 2.x to Java 21 with Spring Boot 3.x.

Focus on:
1. Deprecated Java APIs and their modern replacements
2. Spring Boot 2.x to 3.x migration issues (especially javax -> jakarta)
3. Modern Java 21 features that could be applied
4. Performance improvements
5. Code quality improvements

Be concise and actionable.

Code:
```java
{code[:2000]}  // First 2000 chars to keep prompt manageable
```

Provide analysis in this JSON format:
{{
    "critical_issues": [],
    "modernization_opportunities": [],
    "performance_improvements": [],
    "code_quality_suggestions": []
}}
"""

    def _analyze_with_openai(self, prompt: str) -> Optional[str]:
        """Analyze using OpenAI API"""
        try:
            from openai import OpenAI
            client = OpenAI(api_key=self.openai_api_key)
            
            response = client.chat.completions.create(
                model="gpt-4-turbo-preview",
                messages=[
                    {"role": "system", "content": "You are a Java modernization expert."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=500
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"OpenAI analysis failed: {str(e)}")
            return None

    def _analyze_with_anthropic(self, prompt: str) -> Optional[str]:
        """Analyze using Anthropic Claude API"""
        try:
            from anthropic import Anthropic
            client = Anthropic(api_key=self.anthropic_api_key)
            
            message = client.messages.create(
                model="claude-3-opus-20240229",
                max_tokens=500,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            return message.content[0].text
        except Exception as e:
            logger.error(f"Anthropic analysis failed: {str(e)}")
            return None


class GenAIService:
    """
    Main service that scans Java projects and modernizes them using the JavaModernizer
    and optional LLM analysis
    """

    def __init__(self):
        self.llm_service = LLMService()
        self.java_modernizer = java_modernizer

    def analyze_code(self, request: ScanRequest) -> ScanResult:
        """
        Scans a Java project and creates a modernized version
        """
        logger.info(f"Starting analysis for project: {request.project_path}")
        
        # Validate project path
        if not os.path.exists(request.project_path):
            logger.error(f"Project path does not exist: {request.project_path}")
            return ScanResult(
                request=request,
                output_path="",
                status="failed",
                error_message=f"Project path does not exist: {request.project_path}"
            )

        # Create output directory
        output_path = f"{request.project_path}_modernized"
        if os.path.exists(output_path):
            shutil.rmtree(output_path)
        os.makedirs(output_path)

        # Initialize analysis results
        project_analysis = ProjectAnalysis()
        file_analyses = []

        # Scan all Java files
        java_files = self._find_java_files(request.project_path)
        logger.info(f"Found {len(java_files)} Java files")

        for file_path in java_files:
            try:
                analysis = self._analyze_and_modernize_file(
                    file_path, 
                    request.project_path, 
                    output_path,
                    request.use_ai,
                    request.ai_provider
                )
                file_analyses.append(analysis)
                project_analysis.total_files_analyzed += 1
                project_analysis.issues_found += len(analysis.issues)
            except Exception as e:
                logger.error(f"Error processing {file_path}: {str(e)}")

        # Scan for build files
        self._analyze_build_files(request.project_path, project_analysis)

        # Copy non-Java files
        self._copy_non_java_files(request.project_path, output_path)

        # Compile results
        project_analysis.file_analyses = file_analyses
        
        result = ScanResult(
            request=request,
            output_path=output_path,
            project_analysis=project_analysis,
            status="completed"
        )
        
        # Generate HTML report
        reports_dir = os.path.join(output_path, "reports")
        if html_report_generator.generate_full_report(result.__dict__, reports_dir):
            logger.info(f"HTML report generated at {reports_dir}")

        logger.info(f"Analysis complete. Output at: {output_path}")
        return result

    def _find_java_files(self, project_path: str) -> list:
        """Find all .java files in the project"""
        java_files = []
        for root, dirs, files in os.walk(project_path):
            # Skip output directories
            dirs[:] = [d for d in dirs if not d.endswith("_modernized")]
            
            for file in files:
                if file.endswith(".java"):
                    java_files.append(os.path.join(root, file))
        return java_files

    def _analyze_and_modernize_file(
        self, 
        file_path: str, 
        project_path: str,
        output_path: str,
        use_ai: bool,
        ai_provider: str
    ) -> FileAnalysis:
        """Analyze and modernize a single Java file"""
        
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()

        # Get static analysis
        analysis = self.java_modernizer.analyze_java_file(content, os.path.basename(file_path))

        # Get AI analysis if enabled
        ai_analysis = None
        if use_ai:
            ai_analysis = self.llm_service.analyze_code_with_ai(
                content, 
                os.path.basename(file_path),
                ai_provider
            )

        # Modernize the code
        modernized_content = self.java_modernizer.modernize_java_code(content, os.path.basename(file_path))

        # Write modernized file
        relative_path = os.path.relpath(file_path, project_path)
        new_file_path = os.path.join(output_path, relative_path)
        os.makedirs(os.path.dirname(new_file_path), exist_ok=True)
        
        with open(new_file_path, "w", encoding="utf-8") as f:
            f.write(modernized_content)

        # Create analysis result
        file_analysis = FileAnalysis(
            filename=os.path.basename(file_path),
            filepath=relative_path,
            issues=analysis["issues"],
            suggestions=analysis["suggestions"],
            transformations=analysis["transformations"],
            ai_analysis=ai_analysis
        )

        return file_analysis

    def _analyze_build_files(self, project_path: str, project_analysis: ProjectAnalysis) -> None:
        """Analyze Maven pom.xml or Gradle build.gradle"""
        
        # Check for pom.xml
        pom_path = os.path.join(project_path, "pom.xml")
        if os.path.exists(pom_path):
            with open(pom_path, "r", encoding="utf-8", errors="ignore") as f:
                pom_content = f.read()
            
            pom_analysis = self.java_modernizer.analyze_pom_xml(pom_content)
            project_analysis.build_file_type = "maven"
            project_analysis.dependency_issues.extend(pom_analysis["issues"])
            project_analysis.dependency_upgrades.update(pom_analysis["upgrades"])
            project_analysis.build_recommendations.extend(pom_analysis["recommendations"])
            
            # Analyze properties if present
            pom_config = config_analyzer.analyze_pom_xml_properties(pom_content)
            project_analysis.dependency_issues.extend(pom_config.get("issues", []))

        # Check for build.gradle
        gradle_path = os.path.join(project_path, "build.gradle")
        if os.path.exists(gradle_path):
            with open(gradle_path, "r", encoding="utf-8", errors="ignore") as f:
                gradle_content = f.read()
            
            gradle_analysis = self.java_modernizer.analyze_build_gradle(gradle_content)
            project_analysis.build_file_type = "gradle"
            project_analysis.dependency_issues.extend(gradle_analysis["issues"])
            project_analysis.dependency_upgrades.update(gradle_analysis["upgrades"])
            project_analysis.build_recommendations.extend(gradle_analysis["recommendations"])
            
            # Analyze Gradle properties
            gradle_config = config_analyzer.analyze_gradle_properties(gradle_content)
            project_analysis.dependency_issues.extend(gradle_config.get("issues", []))
        
        # Analyze application.properties
        app_properties_path = os.path.join(project_path, "src/main/resources/application.properties")
        if os.path.exists(app_properties_path):
            props_analysis = config_analyzer.analyze_config_file(app_properties_path)
            if props_analysis:
                project_analysis.dependency_issues.extend(props_analysis.get("issues", []))
                project_analysis.build_recommendations.extend(props_analysis.get("recommendations", []))
        
        # Analyze application.yml/yaml
        for yml_file in ["application.yml", "application.yaml"]:
            app_yml_path = os.path.join(project_path, f"src/main/resources/{yml_file}")
            if os.path.exists(app_yml_path):
                yml_analysis = config_analyzer.analyze_config_file(app_yml_path)
                if yml_analysis:
                    project_analysis.dependency_issues.extend(yml_analysis.get("issues", []))
                    project_analysis.build_recommendations.extend(yml_analysis.get("recommendations", []))

    def _copy_non_java_files(self, project_path: str, output_path: str) -> None:
        """Copy non-Java files to maintain project structure and update build files"""
        for root, dirs, files in os.walk(project_path):
            # Skip output directories
            dirs[:] = [d for d in dirs if not d.endswith("_modernized")]
            
            for file in files:
                if not file.endswith(".java"):
                    src_file = os.path.join(root, file)
                    rel_path = os.path.relpath(src_file, project_path)
                    dst_file = os.path.join(output_path, rel_path)
                    
                    os.makedirs(os.path.dirname(dst_file), exist_ok=True)
                    try:
                        shutil.copy2(src_file, dst_file)
                    except Exception as e:
                        logger.warning(f"Could not copy {src_file}: {str(e)}")
        
        # Update pom.xml after copying
        pom_path = os.path.join(output_path, "pom.xml")
        if os.path.exists(pom_path):
            success, message, changes = pom_updater.update_pom_xml(pom_path)
            if success and len(changes) > 0:
                logger.info(f"Updated pom.xml: {len(changes)} changes")
            else:
                logger.info("No pom.xml updates needed")
        
        # Update build.gradle after copying
        gradle_path = os.path.join(output_path, "build.gradle")
        if os.path.exists(gradle_path):
            success, message, changes = gradle_updater.update_build_gradle(gradle_path)
            if success and len(changes) > 0:
                logger.info(f"Updated build.gradle: {len(changes)} changes")
            else:
                logger.info("No build.gradle updates needed")


genai_service = GenAIService()
