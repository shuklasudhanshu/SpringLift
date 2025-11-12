# SpringLift - Complete Usage Guide

## Quick Start

### 1. Installation
```bash
# Clone or navigate to project
cd SpringLift

# Install dependencies
pip install -r requirements.txt

# Create .env file with API keys (optional but recommended)
cp .env.example .env

# Edit .env and add your API keys:
# OPENAI_API_KEY=sk-xxx
# ANTHROPIC_API_KEY=sk-ant-xxx
```

### 2. Start the Server
```bash
uvicorn springlift.main:app --reload
```

The API will be available at: `http://localhost:8000`
Swagger UI: `http://localhost:8000/docs`

## API Examples

### Example 1: Scan a Local Java Project

**Without AI (Static Analysis Only)**
```bash
curl -X POST "http://localhost:8000/scan" \
  -H "Content-Type: application/json" \
  -d '{
    "project_path": "/home/user/my-legacy-app",
    "use_ai": false,
    "ai_provider": "openai"
  }'
```

**With AI (Requires API Key)**
```bash
curl -X POST "http://localhost:8000/scan" \
  -H "Content-Type: application/json" \
  -d '{
    "project_path": "/home/user/my-legacy-app",
    "use_ai": true,
    "ai_provider": "openai"
  }'
```

**Response:**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "request": {
    "project_path": "/home/user/my-legacy-app",
    "use_ai": true,
    "ai_provider": "openai"
  },
  "output_path": "/home/user/my-legacy-app_modernized",
  "project_analysis": {
    "file_analyses": [
      {
        "filename": "UserController.java",
        "filepath": "src/main/java/com/app/UserController.java",
        "issues": [
          "javax.servlet imports found - Migrate to jakarta.servlet for Spring Boot 3.x",
          "Manual null checks found - Consider using Optional or records with validation"
        ],
        "suggestions": [
          "Use records for immutable data classes",
          "Use var keyword for local variable type inference"
        ],
        "transformations": {
          "javax_to_jakarta": {
            "description": "Migrated javax.* imports to jakarta.*",
            "count": 3
          }
        },
        "ai_analysis": "This controller can be simplified using records for DTO classes and patterns...",
        "java_version_target": "21",
        "spring_boot_target": "3.x"
      }
    ],
    "dependency_issues": [
      "Spring Boot 2.7.15 detected - Upgrade to 3.x required",
      "Java 11 detected - Upgrade to 21 recommended"
    ],
    "dependency_upgrades": {
      "spring-boot-starter": "3.x",
      "spring-boot-starter-web": "3.x",
      "java.version": "21"
    },
    "build_file_type": "maven",
    "build_recommendations": [
      "Upgrade Spring Boot from 2.x to 3.x",
      "Upgrade Java from 8/11 to 21",
      "Update all spring-boot-starter dependencies"
    ],
    "total_files_analyzed": 25,
    "issues_found": 48,
    "total_transformations": 23
  },
  "created_at": "2024-11-11T10:30:00",
  "status": "completed",
  "error_message": null
}
```

### Example 2: Retrieve Previously Saved Results

```bash
curl -X GET "http://localhost:8000/scan/550e8400-e29b-41d4-a716-446655440000"
```

### Example 3: Check Server Health

```bash
curl -X GET "http://localhost:8000/health"
```

Response:
```json
{
  "status": "healthy",
  "service": "SpringLift",
  "version": "2.0.0"
}
```

## Understanding the Output

### Project Analysis Structure

#### File Analyses
Each Java file gets analyzed with:
- **Issues**: Problems found that block modernization or are deprecated
- **Suggestions**: Recommended improvements and modern patterns
- **Transformations**: Automated changes that were applied
- **AI Analysis**: Detailed AI insights (if enabled)

Example issues found:
- "javax.* imports found - Must be replaced with jakarta.* for Spring Boot 3.x"
- "Deprecated API found - Use HttpClient (Java 11+)"
- "Anonymous inner classes found - Consider using lambda expressions"

#### Dependency Analysis
- **dependency_issues**: Critical issues with current versions
- **dependency_upgrades**: Recommended version upgrades
- **build_file_type**: Maven (pom.xml) or Gradle (build.gradle)
- **build_recommendations**: Specific steps for build file migration

#### Transformations Applied
Shows what was automatically changed in the code:
```json
"transformations": {
  "javax_to_jakarta": {
    "description": "Migrated javax.* imports to jakarta.*",
    "count": 5
  },
  "pojo_to_records": {
    "description": "Convert POJO classes to records",
    "classes": ["UserDTO", "OrderDTO", "ProductDTO"]
  }
}
```

## Accessing Modernized Code

After scanning, the modernized project is available at:
```
{original_path}_modernized/
```

Example:
- Original: `/home/user/my-legacy-app/`
- Modernized: `/home/user/my-legacy-app_modernized/`

The structure is preserved, with all `.java` files upgraded and all other files copied.

## Configuration Options

### Environment Variables

Create a `.env` file:

```env
# OpenAI Configuration
OPENAI_API_KEY=sk-your-key-here

# Anthropic Configuration  
ANTHROPIC_API_KEY=sk-ant-your-key-here

# Logging
LOG_LEVEL=INFO  # Can be DEBUG, INFO, WARNING, ERROR

# Application Limits
PROJECT_SCAN_MAX_SIZE_MB=1000
MAX_FILES_TO_ANALYZE=10000
```

### Request Parameters

**ScanRequest**:
- `project_path` (required): Absolute path to Java project
- `use_ai` (optional): Enable AI analysis (default: true)
- `ai_provider` (optional): "openai" or "anthropic" (default: "openai")

## AI Providers

### OpenAI GPT-4

**Setup**:
1. Get API key from https://platform.openai.com/api-keys
2. Add to `.env`: `OPENAI_API_KEY=sk-xxx`
3. Use in request: `"ai_provider": "openai"`

**Cost**: ~$0.01-0.03 per scan (depending on project size)

**Advantages**:
- Excellent code understanding
- Comprehensive analysis
- Fast responses

### Anthropic Claude 3

**Setup**:
1. Get API key from https://console.anthropic.com/
2. Add to `.env`: `ANTHROPIC_API_KEY=sk-ant-xxx`
3. Use in request: `"ai_provider": "anthropic"`

**Cost**: Similar to OpenAI

**Advantages**:
- Strong reasoning capabilities
- Great for complex migrations
- Good context awareness

### No AI (Static Analysis Only)

If you don't have API keys, the tool still provides:
- Java version syntax detection
- Spring Boot 2.x pattern identification
- Deprecated API scanning
- Automatic code transformation
- Build file analysis

Just set `"use_ai": false` in requests.

## Real-World Examples

### Example 1: Simple Spring Boot REST Controller

**Original Java File**:
```java
import javax.servlet.http.HttpServletRequest;
import org.springframework.web.bind.annotation.RestController;
import org.springframework.web.bind.annotation.GetMapping;

@RestController
public class HelloController {
    
    public String index(HttpServletRequest request) {
        if (request != null) {
            return "Hello, " + request.getRemoteUser();
        }
        return "Hello, World!";
    }
}
```

**Issues Found**:
- "javax.servlet imports found - Migrate to jakarta.servlet for Spring Boot 3.x"
- "Manual null checks found - Consider using Optional or records"

**Modernized Output**:
```java
/*
 * MODERNIZED BY SPRINGLIFT
 * 
 * Upgrades applied:
 * - Target Java Version: 21 (from 8/11)
 * - Target Spring Boot: 3.x (from 2.x)
 * - Namespace: javax.* -> jakarta.*
 * - Deprecated API usage reviewed
 * 
 * Further modernizations recommended:
 * - Replace manual null checks with Optional
 * - Use records for DTO classes
 * - Leverage sealed classes for type hierarchies
 */

import jakarta.servlet.http.HttpServletRequest;
import org.springframework.web.bind.annotation.RestController;
import org.springframework.web.bind.annotation.GetMapping;

@RestController
public class HelloController {
    
    public String index(HttpServletRequest request) {
        if (request != null) {
            return "Hello, " + request.getRemoteUser();
        }
        return "Hello, World!";
    }
}
```

### Example 2: Data Class (POJO)

**Original**:
```java
public class UserDTO {
    private final String id;
    private final String name;
    private final String email;
    
    public UserDTO(String id, String name, String email) {
        this.id = id;
        this.name = name;
        this.email = email;
    }
    
    public String getId() { return id; }
    public String getName() { return name; }
    public String getEmail() { return email; }
}
```

**AI Suggestions**:
- "This class is a perfect candidate for Java 14+ records"
- "Replace with: `record UserDTO(String id, String name, String email) {}`"
- "This eliminates all the boilerplate getter methods"

## Troubleshooting

### Project Not Found
```
Error: {"status":"failed","error_message":"Project path does not exist: /invalid/path"}
```

**Solution**: Ensure you provide an absolute path that exists:
```bash
# Check the path
ls -la /path/to/project

# Use absolute path in request
curl -X POST "http://localhost:8000/scan" \
  -H "Content-Type: application/json" \
  -d '{"project_path": "/absolute/path/to/project", "use_ai": false}'
```

### AI Analysis Not Working
```
AI analysis failed: 401 Unauthorized
```

**Solution**:
1. Check your API key is valid
2. Verify it's set in `.env` file
3. Try without AI first: `"use_ai": false`
4. Check API quota and billing

### Memory Issues with Large Projects
```
MemoryError: Unable to allocate memory
```

**Solution**:
1. Process larger projects in chunks
2. Increase available system memory
3. Use static analysis only: `"use_ai": false`

### Slow Analysis
**Solution**:
- Large projects take longer (normal)
- AI analysis adds ~2-10 seconds per file
- Use static analysis for quick scan: `"use_ai": false`

## Next Steps After Scanning

1. **Review Modernized Code**
   - Compare original vs modernized files
   - Review suggested changes

2. **Update Dependencies**
   - Apply dependency upgrades from report
   - Update pom.xml or build.gradle

3. **Test Changes**
   - Run unit tests
   - Integration tests
   - Manual testing

4. **Deploy**
   - Update CI/CD pipelines
   - Test in staging environment
   - Deploy to production

## Performance Tips

- **Static Analysis Only**: ~1-5 seconds per project
- **With AI Analysis**: +2-10 seconds per file (depends on file size)
- **Large Projects (1000+ files)**: Consider processing in batches

## Support & Documentation

- **API Docs**: http://localhost:8000/docs (Swagger UI)
- **GitHub Issues**: Report bugs or request features
- **Health Check**: http://localhost:8000/health

## Integration Examples

### Python Client
```python
import requests

response = requests.post(
    "http://localhost:8000/scan",
    json={
        "project_path": "/path/to/project",
        "use_ai": True,
        "ai_provider": "openai"
    }
)

result = response.json()
print(f"Scan ID: {result['id']}")
print(f"Output: {result['output_path']}")
print(f"Issues: {result['project_analysis']['issues_found']}")
```

### JavaScript/Node.js
```javascript
const response = await fetch('http://localhost:8000/scan', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    project_path: '/path/to/project',
    use_ai: true,
    ai_provider: 'openai'
  })
});

const result = await response.json();
console.log(`Output: ${result.output_path}`);
```

## Best Practices

1. **Always backup** your original project before applying changes
2. **Review changes** from AI suggestions before accepting
3. **Test thoroughly** after modernization
4. **Use version control** to track changes
5. **Process in stages** for large projects
6. **Monitor costs** if using AI providers
7. **Keep .env file secure** - don't commit API keys to version control

---

For more information, see the main README.md file.
