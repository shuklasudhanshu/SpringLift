# SpringLift

> ⚠️ **This project is under active development — contributions welcome!** See [CONTRIBUTING.md](CONTRIBUTING.md) for how to contribute.

**SpringLift** is a GenAI-powered tool designed to modernize legacy Java applications. It scans Java 8/11 projects using Spring Boot 2.x and provides AI-powered suggestions and automated transformations to upgrade them to Java 21 with Spring Boot 3.x.

## Features

-   **Smart Project Scanning**: Analyzes entire Java projects for modernization opportunities
-   **AI-Powered Analysis**: Uses OpenAI GPT-4 or Anthropic Claude for intelligent code review and suggestions
-   **Automatic Code Transformation**: Converts Java code with modern language features and Spring Boot 3.x patterns
-   **Dependency Analysis**: Scans Maven (pom.xml) and Gradle (build.gradle) files for version upgrades
-   **Detailed Reporting**: Provides file-by-file analysis with issues, suggestions, and transformations
-   **Framework Upgrades**: Handles javax → jakarta namespace migration for Spring Boot 3.x
-   **Build Support**: Generates modernized versions of your entire project
-   **RESTful API**: Easy-to-use REST interface with auto-generated Swagger documentation

## Project Structure

```
SpringLift/
├── Dockerfile
├── README.md
├── .env.example
├── requirements.txt
├── helm/
│   ├── Chart.yaml
│   └── templates/
│       ├── deployment.yaml
│       └── service.yaml
├── sample_data/
│   ├── legacy_java_code.java
│   └── legacy_python_code.py
├── springlift/
│   ├── __init__.py
│   ├── exceptions.py
│   ├── logger.py
│   ├── main.py
│   ├── models.py
│   ├── services.py
│   ├── storage.py
│   ├── java_modernizer.py
│   └── __pycache__/
└── tests/
    ├── __init__.py
    ├── test_main.py
    └── test_services.py
```

## Setup and Running

### 1. Prerequisites

- Python 3.9+
- pip (Python package manager)
- (Optional) OpenAI API key for AI-powered analysis
- (Optional) Anthropic API key for Claude-based analysis

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure Environment Variables

Copy `.env.example` to `.env` and add your API keys:

```bash
cp .env.example .env
```

Edit `.env` file:
```
OPENAI_API_KEY=sk-your-key-here      # Optional: For OpenAI GPT-4 analysis
ANTHROPIC_API_KEY=sk-ant-your-key    # Optional: For Claude analysis
LOG_LEVEL=INFO
```

**Note**: AI features are optional. The tool works without API keys using static analysis.

### 4. Run the Application

```bash
uvicorn springlift.main:app --reload --host 0.0.0.0 --port 8000
```

The application will be available at `http://127.0.0.1:8000`

## API Usage

### Swagger UI

Interactive API documentation is available at `http://127.0.0.1:8000/docs`

### API Endpoints

#### 1. Scan a Java Project

**Endpoint**: `POST /scan`

Scans a legacy Java project and returns modernization analysis.

**Request Body**:
```json
{
  "project_path": "/path/to/your/java/project",
  "use_ai": true,
  "ai_provider": "openai"
}
```

**Response Example**:
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "request": {
    "project_path": "/path/to/your/java/project",
    "use_ai": true,
    "ai_provider": "openai"
  },
  "output_path": "/path/to/your/java/project_modernized",
  "project_analysis": {
    "file_analyses": [
      {
        "filename": "HelloController.java",
        "filepath": "src/main/java/com/example/HelloController.java",
        "issues": ["javax.* imports found - Must be replaced with jakarta.* for Spring Boot 3.x"],
        "suggestions": ["Use records for immutable data classes"],
        "transformations": {"javax_to_jakarta": {"description": "Migrated javax.* imports to jakarta.*", "count": 2}}
      }
    ],
    "total_files_analyzed": 5,
    "issues_found": 12
  },
  "status": "completed"
}
```

**cURL Example**:
```bash
curl -X POST "http://127.0.0.1:8000/scan" \
  -H "Content-Type: application/json" \
  -d '{
    "project_path": "/path/to/legacy/java/project",
    "use_ai": true,
    "ai_provider": "openai"
  }'
```

#### 2. Retrieve Scan Results

**Endpoint**: `GET /scan/{scan_id}`

```bash
curl -X GET "http://127.0.0.1:8000/scan/550e8400-e29b-41d4-a716-446655440000"
```

#### 3. Health Check

**Endpoint**: `GET /health`

```bash
curl -X GET "http://127.0.0.1:8000/health"
```

## How It Works

### 1. Project Scanning
- Recursively finds all `.java` files
- Identifies `pom.xml` and `build.gradle` files
- Preserves non-Java files in output

### 2. Static Analysis
- Detects Java 8-specific patterns for modernization
- Identifies Spring Boot 2.x patterns and deprecated APIs
- Scans for outdated Java APIs and patterns
- Suggests modern alternatives (records, sealed classes, pattern matching)

### 3. AI-Powered Analysis (Optional)
When enabled with an API key:
- Uses OpenAI GPT-4 or Anthropic Claude
- Provides context-aware modernization recommendations
- Suggests specific code improvements

### 4. Code Transformation
Automatically applies:
- **Namespace Migration**: `javax.*` → `jakarta.*`
- **Spring Annotations**: Updates deprecated annotations
- **Documentation**: Adds modernization comments

### 5. Dependency Analysis
- Spring Boot version detection
- Java version compatibility
- Dependency upgrade recommendations

### 6. Output Generation
Creates a modernized project with:
- All Java files upgraded
- Non-Java files preserved
- Detailed analysis report

## Testing

Run the test suite:

```bash
pytest tests/ -v
```

## Docker Deployment

Build and run:
```bash
docker build -t springlift:latest .
docker run -p 8000:8000 \
  -e OPENAI_API_KEY="sk-your-key" \
  springlift:latest
```

## License

MIT License