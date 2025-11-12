from springlift.services import GenAIService
from springlift.models import ScanRequest

def test_analyze_python_code():
    service = GenAIService()
    request = ScanRequest(code="print('hello')", language="python")
    result = service.analyze_code(request)
    assert len(result.suggestions) == 3
    suggestion_types = {s.suggestion_type for s in result.suggestions}
    assert "Framework Upgrade" in suggestion_types
    assert "Dockerfile" in suggestion_types
    assert "Helm Chart" in suggestion_types

def test_analyze_java_code():
    service = GenAIService()
    request = ScanRequest(code="System.out.println();", language="java")
    result = service.analyze_code(request)
    assert len(result.suggestions) == 3
    suggestion_types = {s.suggestion_type for s in result.suggestions}
    assert "Framework Upgrade" in suggestion_types
    assert "Dockerfile" in suggestion_types
    assert "Helm Chart" in suggestion_types

def test_dockerfile_suggestion_python():
    service = GenAIService()
    request = ScanRequest(code="", language="python")
    suggestion = service._suggest_dockerfile(request)
    assert "python:3.9-slim" in suggestion.suggested_code
    assert "uvicorn" in suggestion.suggested_code

def test_dockerfile_suggestion_java():
    service = GenAIService()
    request = ScanRequest(code="", language="java")
    suggestion = service._suggest_dockerfile(request)
    assert "openjdk:17-jdk-slim" in suggestion.suggested_code
    assert "java -jar" in suggestion.suggested_code
