"""
Configuration File Analyzer
Analyzes Spring Boot configuration files for modernization
"""
import os
import re
from typing import Dict, List, Optional
from .logger import logger


class ConfigurationAnalyzer:
    """
    Analyzes various configuration files for Spring Boot 2.x → 3.x migration
    """
    
    # Spring Boot 2.x → 3.x property changes
    PROPERTY_MIGRATIONS = {
        # Deprecated properties
        "spring.datasource.url": "spring.datasource.url",  # No change but check value
        "spring.jpa.properties.hibernate.dialect": "spring.jpa.database-platform",
        "spring.mvc.view.prefix": "spring.mvc.view.prefix",  # Check with Spring Boot 3 compatibility
        "spring.mvc.view.suffix": "spring.mvc.view.suffix",
        "spring.resources.static-locations": "spring.web.resources.static-locations",
        "logging.level.org.springframework.web": "logging.level.org.springframework.web",
        "server.servlet.context-path": "server.servlet.context-path",
        "management.endpoints.web.base-path": "management.endpoints.web.base-path",
        "spring.jpa.hibernate.ddl-auto": "spring.jpa.hibernate.ddl-auto",
        "spring.h2.console.enabled": "spring.h2.console.enabled",
    }
    
    # Spring Boot 3.x new properties
    SPRING_BOOT_3_PROPERTIES = [
        "spring.threads.virtual.enabled",  # Virtual threads support
        "spring.servlet.multipart.max-file-size",
        "spring.application.name",
    ]
    
    # Deprecated Spring Boot 2.x properties
    DEPRECATED_PROPERTIES = {
        "spring.jpa.properties.hibernate.jdbc.lob.non_contextual_creation": 
            "No longer needed in Spring Boot 3.x",
        "spring.jpa.properties.hibernate.enable_lazy_load_no_trans": 
            "Use spring.jpa.open-in-view instead",
        "spring.datasource.hikari.maximum-pool-size": 
            "Consider using spring.datasource.hikari.pool-name",
    }
    
    @staticmethod
    def analyze_application_properties(content: str) -> Dict:
        """
        Analyze application.properties file
        """
        issues = []
        recommendations = []
        migrations = {}
        
        lines = content.split('\n')
        
        for line_num, line in enumerate(lines, 1):
            # Skip comments and empty lines
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            
            # Parse property
            if '=' in line:
                key, value = line.split('=', 1)
                key = key.strip()
                value = value.strip()
                
                # Check for deprecated properties
                if key in ConfigurationAnalyzer.DEPRECATED_PROPERTIES:
                    issues.append({
                        "line": line_num,
                        "property": key,
                        "severity": "warning",
                        "message": f"Property '{key}' is deprecated in Spring Boot 3.x",
                        "suggestion": ConfigurationAnalyzer.DEPRECATED_PROPERTIES[key]
                    })
                
                # Check for property migrations
                if key in ConfigurationAnalyzer.PROPERTY_MIGRATIONS:
                    new_key = ConfigurationAnalyzer.PROPERTY_MIGRATIONS[key]
                    if key != new_key:
                        migrations[key] = new_key
                        recommendations.append({
                            "property": key,
                            "new_property": new_key,
                            "current_value": value,
                            "suggestion": f"Migrate property from '{key}' to '{new_key}'"
                        })
                
                # Check for Java version in properties
                if "java.version" in key or "source.encoding" in key:
                    if not value or value == "1.8" or value == "8" or value == "11":
                        recommendations.append({
                            "property": key,
                            "current_value": value,
                            "suggestion": f"Update Java version to 21"
                        })
        
        return {
            "file_type": "properties",
            "issues": issues,
            "migrations": migrations,
            "recommendations": recommendations
        }
    
    @staticmethod
    def analyze_application_yaml(content: str) -> Dict:
        """
        Analyze application.yml/application.yaml file
        """
        issues = []
        recommendations = []
        migrations = {}
        
        lines = content.split('\n')
        
        for line_num, line in enumerate(lines, 1):
            # Skip comments and empty lines
            stripped = line.strip()
            if not stripped or stripped.startswith('#'):
                continue
            
            # Parse YAML key-value pairs (simple parsing for common patterns)
            if ':' in stripped and not stripped.startswith('-'):
                key_part = stripped.split(':')[0].strip()
                
                # Check for deprecated or migration-needed keys
                for prop_key in ConfigurationAnalyzer.DEPRECATED_PROPERTIES:
                    if key_part.endswith(prop_key.split('.')[-1]):
                        issues.append({
                            "line": line_num,
                            "content": stripped,
                            "severity": "warning",
                            "message": f"Potentially deprecated property: {key_part}",
                            "suggestion": ConfigurationAnalyzer.DEPRECATED_PROPERTIES.get(prop_key, "")
                        })
        
        return {
            "file_type": "yaml",
            "issues": issues,
            "migrations": migrations,
            "recommendations": recommendations
        }
    
    @staticmethod
    def analyze_pom_xml_properties(content: str) -> Dict:
        """
        Extract and analyze properties from pom.xml
        """
        issues = []
        recommendations = []
        properties = {}
        
        # Extract properties section
        properties_match = re.search(r'<properties>(.*?)</properties>', content, re.DOTALL)
        if properties_match:
            properties_content = properties_match.group(1)
            
            # Extract individual properties
            prop_matches = re.findall(r'<(\w+)>([^<]+)</\1>', properties_content)
            
            for prop_name, prop_value in prop_matches:
                properties[prop_name] = prop_value
                
                # Check Java version
                if 'java' in prop_name.lower() and 'version' in prop_name.lower():
                    if prop_value in ['1.8', '8', '11']:
                        recommendations.append({
                            "property": prop_name,
                            "current_value": prop_value,
                            "suggested_value": "21",
                            "message": f"Update Java version from {prop_value} to 21"
                        })
                
                # Check Spring Boot version
                if 'spring.boot' in prop_name.lower():
                    if prop_value.startswith('2.'):
                        recommendations.append({
                            "property": prop_name,
                            "current_value": prop_value,
                            "suggested_value": "3.0.0+",
                            "message": f"Update Spring Boot from {prop_value} to 3.x"
                        })
        
        return {
            "file_type": "pom.xml",
            "properties": properties,
            "issues": issues,
            "recommendations": recommendations
        }
    
    @staticmethod
    def analyze_gradle_properties(content: str) -> Dict:
        """
        Analyze build.gradle for configuration needs
        """
        issues = []
        recommendations = []
        config = {}
        
        # Extract Java version
        java_version_match = re.search(r"sourceCompatibility\s*=\s*['\"]([^'\"]+)['\"]", content)
        if java_version_match:
            java_version = java_version_match.group(1)
            config['sourceCompatibility'] = java_version
            
            if java_version in ['1.8', '8', '11']:
                recommendations.append({
                    "property": "sourceCompatibility",
                    "current_value": java_version,
                    "suggested_value": "21",
                    "message": f"Update sourceCompatibility from {java_version} to 21"
                })
        
        # Extract targetCompatibility
        target_version_match = re.search(r"targetCompatibility\s*=\s*['\"]([^'\"]+)['\"]", content)
        if target_version_match:
            target_version = target_version_match.group(1)
            config['targetCompatibility'] = target_version
            
            if target_version in ['1.8', '8', '11']:
                recommendations.append({
                    "property": "targetCompatibility",
                    "current_value": target_version,
                    "suggested_value": "21",
                    "message": f"Update targetCompatibility from {target_version} to 21"
                })
        
        # Check Spring Boot version in dependencies
        spring_boot_match = re.search(r"'org\.springframework\.boot:spring-boot-gradle-plugin:([^'\"]+)'", content)
        if spring_boot_match:
            version = spring_boot_match.group(1)
            config['spring_boot_version'] = version
            
            if version.startswith('2.'):
                recommendations.append({
                    "dependency": "spring-boot-gradle-plugin",
                    "current_version": version,
                    "suggested_version": "3.0.0+",
                    "message": f"Update Spring Boot Gradle plugin from {version} to 3.x"
                })
        
        return {
            "file_type": "build.gradle",
            "config": config,
            "issues": issues,
            "recommendations": recommendations
        }
    
    @staticmethod
    def analyze_config_file(file_path: str) -> Optional[Dict]:
        """
        Analyze a configuration file and return results
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            filename = os.path.basename(file_path)
            
            if filename == 'application.properties':
                return ConfigurationAnalyzer.analyze_application_properties(content)
            
            elif filename in ['application.yml', 'application.yaml']:
                return ConfigurationAnalyzer.analyze_application_yaml(content)
            
            elif filename == 'pom.xml':
                return ConfigurationAnalyzer.analyze_pom_xml_properties(content)
            
            elif filename == 'build.gradle':
                return ConfigurationAnalyzer.analyze_gradle_properties(content)
            
            else:
                logger.warning(f"Unknown configuration file type: {filename}")
                return None
        
        except Exception as e:
            logger.error(f"Error analyzing config file {file_path}: {str(e)}")
            return None


# Singleton instance
config_analyzer = ConfigurationAnalyzer()
