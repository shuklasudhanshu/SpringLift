"""
Gradle build.gradle Updater
Updates dependency versions and properties in build.gradle for modernization
"""
import re
from typing import Dict, List, Optional, Tuple
from .logger import logger


class GradleUpdater:
    """
    Updates Gradle build.gradle files to modernize dependencies and Java versions
    Handles upgrading to Java 21 and Spring Boot 3.x
    """

    # Dependency version mappings for modernization
    DEPENDENCY_VERSIONS = {
        # Spring Boot 3.x
        'spring-boot': '3.2.0',
        
        # Spring Framework 6.x
        'org.springframework:spring-context': '6.1.0',
        'org.springframework:spring-core': '6.1.0',
        'org.springframework.data:spring-data-jpa': '3.2.0',
        'org.springframework:spring-web': '6.1.0',
        'org.springframework:spring-webmvc': '6.1.0',
        'org.springframework.security:spring-security-core': '6.2.0',
        'org.springframework.security:spring-security-web': '6.2.0',
        
        # Spring Cloud
        'org.springframework.cloud:spring-cloud-starter-netflix-eureka-client': '4.1.0',
        'org.springframework.cloud:spring-cloud-starter-config': '4.1.0',
        
        # Jackson (JSON processing)
        'com.fasterxml.jackson.core:jackson-databind': '2.15.2',
        'com.fasterxml.jackson.core:jackson-core': '2.15.2',
        'com.fasterxml.jackson.core:jackson-annotations': '2.15.2',
        
        # Testing
        'org.junit.jupiter:junit-jupiter': '5.9.3',
        'org.mockito:mockito-core': '5.3.0',
        'org.mockito:mockito-junit-jupiter': '5.3.0',
        
        # Logging
        'ch.qos.logback:logback-classic': '1.4.11',
        'org.slf4j:slf4j-api': '2.0.7',
    }

    def update_build_gradle(self, gradle_path: str) -> Tuple[bool, str, List[str]]:
        """
        Update build.gradle with modernized versions
        Returns: (success, message, changes_made)
        """
        try:
            with open(gradle_path, 'r', encoding='utf-8') as f:
                gradle_content = f.read()
            
            original_content = gradle_content
            changes = []

            # Update Java version (sourceCompatibility/targetCompatibility)
            gradle_content, java_changes = self._update_java_version(gradle_content)
            changes.extend(java_changes)

            # Update Spring Boot plugin version
            gradle_content, boot_changes = self._update_spring_boot_plugin(gradle_content)
            changes.extend(boot_changes)

            # Update dependencies
            gradle_content, dep_changes = self._update_dependencies(gradle_content)
            changes.extend(dep_changes)

            # Write updated content if there are actual changes
            if gradle_content != original_content:
                # Add modernization comment ONLY if we're making changes
                gradle_content = self._add_modernization_comment_internal(gradle_content)
                
                with open(gradle_path, 'w', encoding='utf-8') as f:
                    f.write(gradle_content)
                logger.info(f"Updated build.gradle: {len(changes)} changes made")
                return True, f"Successfully updated build.gradle with {len(changes)} changes", changes
            else:
                # No changes needed - don't touch the file at all
                logger.info("No changes needed in build.gradle")
                return True, "build.gradle is already up to date", []

        except Exception as e:
            error_msg = f"Error updating build.gradle: {str(e)}"
            logger.error(error_msg)
            return False, error_msg, []

    def _update_java_version(self, content: str) -> Tuple[str, List[str]]:
        """Update Java version to 21"""
        changes = []

        # Update sourceCompatibility
        pattern = r"sourceCompatibility\s*=\s*['\"]?[\d\.]+['\"]?"
        if re.search(pattern, content):
            content = re.sub(pattern, "sourceCompatibility = '21'", content)
            changes.append("Updated sourceCompatibility to 21")
        else:
            # Check if it's in a different format (like JavaVersion.VERSION_XX)
            pattern = r"sourceCompatibility\s*=\s*JavaVersion\.VERSION_\d+"
            if re.search(pattern, content):
                content = re.sub(pattern, "sourceCompatibility = JavaVersion.VERSION_21", content)
                changes.append("Updated sourceCompatibility to Java 21")

        # Update targetCompatibility
        pattern = r"targetCompatibility\s*=\s*['\"]?[\d\.]+['\"]?"
        if re.search(pattern, content):
            content = re.sub(pattern, "targetCompatibility = '21'", content)
            changes.append("Updated targetCompatibility to 21")
        else:
            # Check if it's in a different format (like JavaVersion.VERSION_XX)
            pattern = r"targetCompatibility\s*=\s*JavaVersion\.VERSION_\d+"
            if re.search(pattern, content):
                content = re.sub(pattern, "targetCompatibility = JavaVersion.VERSION_21", content)
                changes.append("Updated targetCompatibility to Java 21")

        return content, changes

    def _update_spring_boot_plugin(self, content: str) -> Tuple[str, List[str]]:
        """Update Spring Boot Gradle plugin version"""
        changes = []

        # Update spring-boot plugin id
        pattern = r"id\s+['\"]org\.springframework\.boot['\"]\s+version\s+['\"][\d\.]+['\"]"
        if re.search(pattern, content):
            content = re.sub(
                r"(id\s+['\"]org\.springframework\.boot['\"]\s+version\s+)['\"][\d\.]+['\"]",
                r"\g<1>'3.2.0'",
                content
            )
            changes.append("Updated Spring Boot plugin to 3.2.0")

        return content, changes

    def _update_dependencies(self, content: str) -> Tuple[str, List[str]]:
        """Update Spring Boot and framework dependency versions"""
        changes = []

        # Handle various dependency declaration formats in Gradle
        
        # Format 1: 'group:name:version'
        for dep_full, new_version in self.DEPENDENCY_VERSIONS.items():
            if ':' in dep_full:
                group, name = dep_full.rsplit(':', 1)
                pattern = rf"['\"]?{re.escape(group)}:{re.escape(name)}:[^['\"]]+['\"]?"
                
                matches = list(re.finditer(pattern, content))
                if matches:
                    for match in matches:
                        old_dep = match.group(0)
                        new_dep = f"'{group}:{name}:{new_version}'"
                        content = content.replace(old_dep, new_dep, 1)
                        changes.append(f"Updated {name} to {new_version}")

        return content, changes

    def _add_modernization_comment_internal(self, content: str) -> str:
        """Add modernization comment to content string (internal use during update)"""
        # Check if comment already exists
        if 'MODERNIZED by SpringLift' in content:
            return content
        
        # Add comment at the top
        comment = '// MODERNIZED by SpringLift v2.1.1 - Updated to Java 21 and Spring Boot 3.x\n'
        content = comment + content
        return content

    def add_modernization_comment(self, gradle_path: str) -> bool:
        """Add a comment noting this was modernized (only call if file was modified separately)"""
        try:
            with open(gradle_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Check if comment already exists
            if 'MODERNIZED by SpringLift' in content:
                return True
            
            # Add comment at the top
            comment = '// MODERNIZED by SpringLift v2.1.1 - Updated to Java 21 and Spring Boot 3.x\n'
            content = comment + content
            
            with open(gradle_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            logger.info(f"Added modernization comment to {gradle_path}")
            return True
        except Exception as e:
            logger.error(f"Error adding comment to build.gradle: {str(e)}")
            return False

    def get_gradle_info(self, gradle_path: str) -> Dict:
        """Extract key information from build.gradle"""
        info = {
            'project_name': None,
            'current_java_version': None,
            'current_spring_boot_version': None,
            'dependencies': []
        }
        
        try:
            with open(gradle_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Extract Java version
            match = re.search(r"sourceCompatibility\s*=\s*['\"]?([\d\.]+)['\"]?", content)
            if match:
                info['current_java_version'] = match.group(1)
            else:
                match = re.search(r"sourceCompatibility\s*=\s*JavaVersion\.VERSION_(\d+)", content)
                if match:
                    info['current_java_version'] = match.group(1)
            
            # Extract Spring Boot version
            match = re.search(
                r"id\s+['\"]org\.springframework\.boot['\"]\s+version\s+['\"]([^'\"]+)['\"]",
                content
            )
            if match:
                info['current_spring_boot_version'] = match.group(1)
            
            # Extract dependencies
            dep_pattern = r"['\"]?([^:'\"\s]+):([^:'\"\s]+):([^'\"]+)['\"]?"
            for match in re.finditer(dep_pattern, content):
                info['dependencies'].append({
                    'group': match.group(1),
                    'name': match.group(2),
                    'version': match.group(3)
                })
            
            return info
        except Exception as e:
            logger.error(f"Error reading build.gradle info: {str(e)}")
            return info


# Global instance
gradle_updater = GradleUpdater()
