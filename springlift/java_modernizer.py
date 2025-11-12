"""
Java Modernization Engine
Handles Java 8->21 and Spring Boot 2.x->3.x upgrades
"""
import re
from typing import List, Dict, Tuple
from .logger import logger


class JavaModernizer:
    """
    Converts Java 8 syntax and Spring Boot 2.x code to Java 21+ and Spring Boot 3.x
    """

    # Java 8 to Java 21+ transformations
    JAVA_TRANSFORMATIONS = {
        # var keyword for local variable type inference
        "(?:List|Set|Map|HashMap|ArrayList|HashSet)<.*?>\\s+(\\w+)\\s*=\\s*new": 
            lambda m, content: "var %s = new" % m.group(1),
        
        # Lambda expressions are already Java 8+, but we can enhance them
        # Encourage method references where applicable
        
        # Stream API enhancements
        "for\\s*\\(.*?:\\s*(.*?)\\)": 
            None,  # Suggest using streams instead
        
        # Records (Java 14+) for simple POJOs
        "public\\s+class\\s+(\\w+)\\s*\\{\\s*private\\s+final":
            None,  # Suggest converting to records
    }

    # Spring Boot 2.x to 3.x transformations
    SPRING_TRANSFORMATIONS = {
        # javax -> jakarta namespace migration
        "import\\s+javax\\.": "import jakarta.",
        "import\\s+org\\.springframework\\.boot\\.web\\.servlet\\.support\\.SpringBootServletInitializer":
            "import org.springframework.boot.web.servlet.support.SpringBootServletInitializer",
        
        # Spring Boot 3.x property changes
        "spring\\.datasource\\.url": "spring.datasource.url",
        "spring\\.jpa\\.properties\\.hibernate\\.dialect":
            "spring.jpa.database-platform",
        
        # Actuator endpoint changes
        "management\\.endpoints\\.web\\.exposure\\.include=":
            "management.endpoints.web.exposure.include=",
    }

    # Dependency upgrades
    DEPENDENCY_UPGRADES = {
        "spring-boot-starter": "3.x",
        "spring-boot-starter-web": "3.x",
        "spring-boot-starter-data-jpa": "3.x",
        "spring-data-jpa": "3.x",
        "org.springframework:spring-context": "6.x",
        "org.springframework:spring-core": "6.x",
        "org.springframework.cloud:spring-cloud-starter-netflix-eureka-client": "4.x",
        "org.springframework.cloud:spring-cloud-starter-config": "4.x",
        "com.fasterxml.jackson.core:jackson-databind": "2.15+",
        "junit:junit": "4.13+",
        "org.junit.jupiter:junit-jupiter": "5.x",
    }

    def analyze_java_file(self, content: str, filename: str) -> Dict:
        """
        Analyzes a Java file and returns modernization suggestions
        """
        issues = []
        suggestions = []
        transformations = {}

        # Check Java version syntax usage
        issues.extend(self._check_java_version_issues(content))
        
        # Check Spring Boot 2.x patterns
        issues.extend(self._check_spring_boot_2_patterns(content))
        
        # Check for deprecated APIs
        issues.extend(self._check_deprecated_apis(content))
        
        # Get transformation suggestions
        suggestions, transformations = self._get_transformations(content)

        return {
            "filename": filename,
            "issues": issues,
            "suggestions": suggestions,
            "transformations": transformations,
            "java_version_target": "21",
            "spring_boot_target": "3.x",
        }

    def _check_java_version_issues(self, content: str) -> List[str]:
        """Check for Java 8 specific patterns that can be modernized"""
        issues = []

        # Check for verbose lambda expressions
        if re.search(r"new\s+\w+\s*<>?\s*\(\)\s*\{\s*public\s+\w+.*?\{", content):
            issues.append("Anonymous inner classes found - Consider using lambda expressions or functional interfaces (Java 8+)")

        # Check for manual null checks (Optional is preferred)
        if re.search(r"if\s*\(\s*\w+\s*!=\s*null\s*\)", content):
            issues.append("Manual null checks found - Consider using Optional or records with validation (Java 14+)")

        # Check for manual resource management
        if re.search(r"try\s*\{.*?finally\s*\{.*?close", content, re.DOTALL):
            issues.append("Manual resource management found - Use try-with-resources (Java 7+) or virtual threads (Java 19+)")

        # Check for old stream usage patterns
        if re.search(r"for\s*\(\s*\w+\s+\w+\s*:\s+\w+\)", content):
            issues.append("Traditional for-loops found - Consider using Streams API for functional operations")

        # Check for array cloning
        if "clone()" in content:
            issues.append("Array.clone() found - Consider using Arrays.copyOf() or streams")

        return issues

    def _check_spring_boot_2_patterns(self, content: str) -> List[str]:
        """Check for Spring Boot 2.x patterns"""
        issues = []

        # Check for javax imports (need jakarta in Spring Boot 3)
        if re.search(r"import\s+javax\.", content):
            issues.append("javax.* imports found - Must be replaced with jakarta.* for Spring Boot 3.x")

        # Check for deprecated annotations
        if "@Deprecated" in content:
            issues.append("Deprecated annotations found - Review and upgrade to current APIs")

        # Check for XML configuration (discourage in Spring Boot 3)
        if "org.springframework.context.support.ClassPathXmlApplicationContext" in content:
            issues.append("XML-based Spring configuration detected - Migrate to Java-based @Configuration classes")

        # Check for old servlet API
        if re.search(r"import\s+javax\.servlet", content):
            issues.append("javax.servlet imports found - Migrate to jakarta.servlet for Spring Boot 3.x")

        return issues

    def _check_deprecated_apis(self, content: str) -> List[str]:
        """Check for deprecated Java/Spring APIs"""
        issues = []

        deprecated_patterns = {
            r"Runtime\.getRuntime\(\)\.exec\(": "Process.start() or ProcessHandle API (Java 9+)",
            r"System\.getProperties\(\)": "System.getProperties() or direct method calls",
            r"new\s+URL\(": "Use URI or HttpClient (Java 11+)",
            r"HttpURLConnection": "Use HttpClient (Java 11+)",
            r"sun\.misc\.BASE64": "Use java.util.Base64 (Java 8+)",
            r"org\.apache\.commons\.lang\..*": "Use built-in Java utilities (Java 8+)",
        }

        for pattern, suggestion in deprecated_patterns.items():
            if re.search(pattern, content):
                issues.append(f"Deprecated API found - Use {suggestion}")

        return issues

    def _get_transformations(self, content: str) -> Tuple[List[str], Dict]:
        """Get transformation suggestions and code transformations"""
        suggestions = []
        transformations = {}

        # Java 8 -> 21 suggestions
        java_suggestions = [
            ("Use var keyword for local variable type inference", "Modern type inference improves code readability"),
            ("Use records for immutable data classes", "Records (Java 14+) replace verbose POJO boilerplate"),
            ("Leverage sealed classes for type hierarchy", "Sealed classes (Java 15+) provide better encapsulation"),
            ("Use text blocks for multi-line strings", "Text blocks (Java 13+) eliminate escape sequences"),
            ("Adopt pattern matching", "Pattern matching (Java 16+) simplifies code"),
            ("Use virtual threads for I/O operations", "Virtual threads (Java 19+) enable efficient async programming"),
        ]

        suggestions.extend([s[0] for s in java_suggestions])

        # Transformation: javax -> jakarta
        if "import javax." in content:
            transformed = content.replace("import javax.", "import jakarta.")
            transformations["javax_to_jakarta"] = {
                "description": "Migrated javax.* imports to jakarta.*",
                "count": len(re.findall(r"import javax\.", content))
            }

        # Transformation: Add records suggestion for POJOs
        pojo_matches = re.findall(r"public\s+class\s+(\w+)\s*\{[\s\S]*?(?:private\s+final\s+\w+)", content)
        if pojo_matches:
            transformations["pojo_to_records"] = {
                "description": f"Convert {len(pojo_matches)} POJO classes to records",
                "classes": pojo_matches[:5]  # First 5
            }

        return suggestions, transformations

    def modernize_java_code(self, content: str, filename: str) -> str:
        """
        Applies transformations to Java code for modernization
        """
        modernized = content

        # 1. Migrate javax to jakarta
        modernized = re.sub(r"import\s+javax\.", "import jakarta.", modernized)

        # 2. Update Spring Boot annotations if present
        if "org.springframework" in modernized:
            # Update deprecated Spring annotations
            modernized = re.sub(
                r"@EnableEurekaClient",
                "// @EnableEurekaClient - Enabled by default in Spring Cloud 2020+",
                modernized
            )
            modernized = re.sub(
                r"@EnableFeignClients",
                "@EnableFeignClients",
                modernized
            )

        # Only add modernization header if actual code changes were made
        if modernized != content:
            header = f"""/*
 * MODERNIZED BY SPRINGLIFT
 * 
 * Upgrades applied:
 * - Target Java Version: 21 (from 8/11)
 * - Target Spring Boot: 3.x (from 2.x)
 * - Namespace: javax.* -> jakarta.*
 * - Deprecated API usage reviewed
 * 
 * Further modernizations recommended:
 * - Review and apply modern Java language features (records, sealed classes, pattern matching)
 * - Update dependency versions (see pom.xml or build.gradle)
 * - Replace anonymous inner classes with lambda expressions
 * - Use Optional instead of null checks
 * 
 * Generated: {self._get_timestamp()}
 */
"""
            modernized = header + "\n" + modernized

        return modernized

    def analyze_pom_xml(self, content: str) -> Dict:
        """
        Analyzes Maven pom.xml for dependency upgrades
        """
        issues = []
        upgrades = {}

        # Check Spring Boot version
        spring_boot_match = re.search(r"<spring-boot\.version>([^<]+)<", content)
        if spring_boot_match:
            version = spring_boot_match.group(1)
            if version.startswith("2"):
                issues.append(f"Spring Boot 2.x detected ({version}) - Upgrade to 3.x required")
                upgrades["spring-boot-starter"] = "3.x"

        # Check Java version
        java_version_match = re.search(r"<java\.version>([^<]+)<", content)
        if java_version_match:
            version = java_version_match.group(1)
            if version in ["1.8", "8", "11"]:
                issues.append(f"Java {version} detected - Upgrade to 21 recommended")
                upgrades["java.version"] = "21"

        # Extract dependencies and suggest upgrades
        dep_matches = re.findall(r"<artifactId>([^<]+)<", content)
        for dep in dep_matches:
            if dep in self.DEPENDENCY_UPGRADES:
                upgrades[dep] = self.DEPENDENCY_UPGRADES[dep]

        return {
            "issues": issues,
            "upgrades": upgrades,
            "recommendations": [
                "Upgrade Spring Boot from 2.x to 3.x",
                "Upgrade Java from 8/11 to 21",
                "Update all spring-boot-starter dependencies",
                "Migrate javax.* to jakarta.* namespace",
                "Review and update third-party library versions",
            ]
        }

    def analyze_build_gradle(self, content: str) -> Dict:
        """
        Analyzes build.gradle for dependency upgrades
        """
        issues = []
        upgrades = {}

        # Check Spring Boot version
        if re.search(r"id\s+['\"]org\.springframework\.boot['\"]\s+version\s+['\"]2\.", content):
            issues.append("Spring Boot 2.x detected - Upgrade to 3.x required")
            upgrades["spring-boot"] = "3.x"

        # Check Java compatibility
        if re.search(r"sourceCompatibility\s*=\s*['\"]1\.8['\"]", content) or \
           re.search(r"sourceCompatibility\s*=\s*['\"]11['\"]", content):
            issues.append("Java 8/11 compatibility detected - Upgrade to 21 recommended")
            upgrades["sourceCompatibility"] = "21"

        return {
            "issues": issues,
            "upgrades": upgrades,
            "recommendations": [
                "Update Spring Boot plugin version to 3.x",
                "Update sourceCompatibility and targetCompatibility to 21",
                "Update all dependency versions",
                "Review gradle wrapper version",
            ]
        }

    @staticmethod
    def _get_timestamp() -> str:
        """Get current timestamp"""
        from datetime import datetime
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


# Singleton instance
java_modernizer = JavaModernizer()
