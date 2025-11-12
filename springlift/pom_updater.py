"""
Maven pom.xml Updater
Updates dependency versions and properties in pom.xml for modernization
"""
import re
import xml.etree.ElementTree as ET
from typing import Dict, List, Optional, Tuple
from .logger import logger


class PomUpdater:
    """
    Updates Maven pom.xml files to modernize dependencies and Java versions
    Handles upgrading to Java 21 and Spring Boot 3.x
    """

    # Namespace for Maven XML
    NS = {'pom': 'http://maven.apache.org/POM/4.0.0'}
    
    # Dependency version mappings for modernization
    DEPENDENCY_VERSIONS = {
        # Spring Boot 3.x
        'spring-boot': '3.2.0',
        'spring-boot-starter': '3.2.0',
        'spring-boot-starter-web': '3.2.0',
        'spring-boot-starter-data-jpa': '3.2.0',
        'spring-boot-starter-security': '3.2.0',
        'spring-boot-starter-actuator': '3.2.0',
        'spring-boot-starter-logging': '3.2.0',
        'spring-boot-starter-test': '3.2.0',
        
        # Spring Framework 6.x
        'spring-context': '6.1.0',
        'spring-core': '6.1.0',
        'spring-data-jpa': '3.2.0',
        'spring-web': '6.1.0',
        'spring-webmvc': '6.1.0',
        'spring-security-core': '6.2.0',
        'spring-security-web': '6.2.0',
        
        # Spring Cloud
        'spring-cloud-starter-netflix-eureka-client': '4.1.0',
        'spring-cloud-starter-config': '4.1.0',
        'spring-cloud-starter-netflix-hystrix': '4.1.0',
        
        # Jackson (JSON processing)
        'jackson-databind': '2.15.2',
        'jackson-core': '2.15.2',
        'jackson-annotations': '2.15.2',
        
        # Testing
        'junit-jupiter': '5.9.3',
        'mockito-core': '5.3.0',
        'mockito-junit-jupiter': '5.3.0',
        
        # Logging
        'logback-classic': '1.4.11',
        'slf4j-api': '2.0.7',
        
        # Utilities
        'jakarta.servlet-api': '6.0.0',
        'jakarta.persistence-api': '3.1.0',
    }

    # Properties to update
    PROPERTIES_UPDATES = {
        'java.version': '21',
        'maven.compiler.source': '21',
        'maven.compiler.target': '21',
        'project.build.sourceEncoding': 'UTF-8',
        'spring-boot.version': '3.2.0',
    }

    def update_pom_xml(self, pom_path: str) -> Tuple[bool, str, List[str]]:
        """
        Update pom.xml with modernized versions
        Returns: (success, message, changes_made)
        """
        try:
            with open(pom_path, 'r', encoding='utf-8') as f:
                pom_content = f.read()
            
            original_content = pom_content
            changes = []

            # Update parent version FIRST (most important for Spring Boot projects)
            pom_content, parent_changes = self._update_parent_version(pom_content)
            changes.extend(parent_changes)

            # Update Java version properties
            pom_content, java_changes = self._update_java_version(pom_content)
            changes.extend(java_changes)

            # Update Spring Boot properties
            pom_content, spring_changes = self._update_spring_boot_version(pom_content)
            changes.extend(spring_changes)

            # Update dependencies in XML
            pom_content, dep_changes = self._update_dependencies(pom_content)
            changes.extend(dep_changes)

            # Update property versions
            pom_content, prop_changes = self._update_properties(pom_content)
            changes.extend(prop_changes)

            # Update Spring Boot Maven Plugin version
            pom_content, plugin_changes = self._update_maven_plugins(pom_content)
            changes.extend(plugin_changes)

            # Write updated content if there are actual changes
            if pom_content != original_content:
                # Add modernization comment ONLY if we're making changes
                pom_content = self._add_modernization_comment_internal(pom_content)
                
                with open(pom_path, 'w', encoding='utf-8') as f:
                    f.write(pom_content)
                logger.info(f"Updated pom.xml: {len(changes)} changes made")
                return True, f"Successfully updated pom.xml with {len(changes)} changes", changes
            else:
                # No changes needed - don't touch the file at all
                logger.info("No changes needed in pom.xml")
                return True, "pom.xml is already up to date", []

        except Exception as e:
            error_msg = f"Error updating pom.xml: {str(e)}"
            logger.error(error_msg)
            return False, error_msg, []

    def _update_parent_version(self, content: str) -> Tuple[str, List[str]]:
        """Update Spring Boot starter-parent version in <parent> section"""
        changes = []
        
        # Match the entire parent section and update version for spring-boot-starter-parent
        # Pattern: <parent>...<artifactId>spring-boot-starter-parent</artifactId>...<version>X.X.X</version>...</parent>
        parent_pattern = r'(<parent>.*?<artifactId>spring-boot-starter-parent</artifactId>.*?<version>)([0-9\.]+)(\.RELEASE)?</version>'
        
        if re.search(parent_pattern, content, re.DOTALL):
            content = re.sub(
                parent_pattern,
                r'\g<1>3.2.0</version>',
                content,
                flags=re.DOTALL
            )
            changes.append("Updated parent spring-boot-starter-parent version to 3.2.0")
        
        return content, changes

    def _update_java_version(self, content: str) -> Tuple[str, List[str]]:
        """Update Java version to 21"""
        changes = []
        
        # Update <java.version>
        pattern = r'<java\.version>.*?</java\.version>'
        if re.search(pattern, content):
            content = re.sub(pattern, '<java.version>21</java.version>', content)
            changes.append("Updated java.version to 21")

        # Update <maven.compiler.source>
        pattern = r'<maven\.compiler\.source>.*?</maven\.compiler\.source>'
        if re.search(pattern, content):
            content = re.sub(pattern, '<maven.compiler.source>21</maven.compiler.source>', content)
            changes.append("Updated maven.compiler.source to 21")
        else:
            # Add if not present
            insert_pos = content.find('</properties>')
            if insert_pos > 0:
                content = content[:insert_pos] + '\n        <maven.compiler.source>21</maven.compiler.source>' + content[insert_pos:]
                changes.append("Added maven.compiler.source property (21)")

        # Update <maven.compiler.target>
        pattern = r'<maven\.compiler\.target>.*?</maven\.compiler\.target>'
        if re.search(pattern, content):
            content = re.sub(pattern, '<maven.compiler.target>21</maven.compiler.target>', content)
            changes.append("Updated maven.compiler.target to 21")
        else:
            # Add if not present
            insert_pos = content.find('</properties>')
            if insert_pos > 0:
                content = content[:insert_pos] + '\n        <maven.compiler.target>21</maven.compiler.target>' + content[insert_pos:]
                changes.append("Added maven.compiler.target property (21)")

        return content, changes

    def _update_spring_boot_version(self, content: str) -> Tuple[str, List[str]]:
        """Update Spring Boot version to 3.x"""
        changes = []
        
        # Update <parent><version> for Spring Boot parent
        # Matches: <parent>...<version>2.x.x</version>...</parent>
        pattern = r'(<parent>.*?<artifactId>spring-boot-starter-parent</artifactId>.*?<version>)[\d\.]+(.RELEASE)?</version>'
        if re.search(pattern, content, re.DOTALL):
            content = re.sub(
                pattern,
                r'\g<1>3.2.0</version>',
                content,
                flags=re.DOTALL
            )
            changes.append("Updated parent spring-boot-starter-parent version to 3.2.0")
        
        # Update spring-boot.version property (if used)
        pattern = r'<spring-boot\.version>.*?</spring-boot\.version>'
        if re.search(pattern, content):
            content = re.sub(pattern, '<spring-boot.version>3.2.0</spring-boot.version>', content)
            changes.append("Updated spring-boot.version property to 3.2.0")

        return content, changes

    def _update_dependencies(self, content: str) -> Tuple[str, List[str]]:
        """Update Spring Boot and framework dependency versions"""
        changes = []
        
        # Update Spring Boot starter dependencies
        for dep_name, new_version in self.DEPENDENCY_VERSIONS.items():
            # Pattern for artifact ID match
            patterns = [
                # Match <version> tag after <artifactId>{dep_name}</artifactId>
                rf'(<artifactId>{dep_name}</artifactId>\s*<version>).*?(</version>)',
                # Alternative pattern with different spacing
                rf'(<artifactId>\s*{dep_name}\s*</artifactId>\s*<version>).*?(</version>)',
            ]
            
            for pattern in patterns:
                matches = list(re.finditer(pattern, content))
                if matches:
                    for match in matches:
                        old_version = match.group(0)
                        new_dep = match.group(1) + new_version + match.group(2)
                        content = content.replace(old_version, new_dep, 1)
                        changes.append(f"Updated {dep_name} to {new_version}")
                    break

        return content, changes

    def _update_properties(self, content: str) -> Tuple[str, List[str]]:
        """Update project properties"""
        changes = []
        
        for prop_name, prop_value in self.PROPERTIES_UPDATES.items():
            # Skip java.version as it's handled separately
            if prop_name == 'java.version':
                continue
            
            pattern = rf'<{prop_name}>.*?</{prop_name}>'
            if re.search(pattern, content):
                content = re.sub(pattern, f'<{prop_name}>{prop_value}</{prop_name}>', content)
                changes.append(f"Updated property {prop_name} to {prop_value}")

        return content, changes

    def _update_maven_plugins(self, content: str) -> Tuple[str, List[str]]:
        """Update Spring Boot Maven Plugin version"""
        changes = []
        
        # Update spring-boot-maven-plugin version
        pattern = r'(<artifactId>spring-boot-maven-plugin</artifactId>\s*<version>).*?(</version>)'
        if re.search(pattern, content):
            content = re.sub(pattern, r'\g<1>3.2.0\2', content)
            changes.append("Updated spring-boot-maven-plugin to 3.2.0")

        # Update maven-compiler-plugin
        pattern = r'(<artifactId>maven-compiler-plugin</artifactId>\s*(?:<version>.*?</version>)?)'
        if '<version>' not in re.search(pattern, content).group(0) if re.search(pattern, content) else False:
            # Add version if not present
            pattern = r'(<artifactId>maven-compiler-plugin</artifactId>)'
            content = re.sub(pattern, r'\1\n                <version>3.11.0</version>', content)
            changes.append("Added maven-compiler-plugin version 3.11.0")

        # Update maven-surefire-plugin
        pattern = r'(<artifactId>maven-surefire-plugin</artifactId>\s*<version>).*?(</version>)'
        if re.search(pattern, content):
            content = re.sub(pattern, r'\g<1>3.1.2\2', content)
            changes.append("Updated maven-surefire-plugin to 3.1.2")

        return content, changes

    def _add_modernization_comment_internal(self, content: str) -> str:
        """Add modernization comment to content string (internal use during update)"""
        # Check if comment already exists
        if 'MODERNIZED by SpringLift' in content:
            return content
        
        # Add comment after XML declaration
        comment = '\n<!-- MODERNIZED by SpringLift v2.1.1 - Updated to Java 21 and Spring Boot 3.x -->\n'
        content = content.replace('?>\n', '?>' + comment, 1)
        return content

    def add_modernization_comment(self, pom_path: str) -> bool:
        """Add a comment noting this was modernized (only call if file was modified separately)"""
        try:
            with open(pom_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Check if comment already exists
            if 'MODERNIZED by SpringLift' in content:
                return True
            
            # Add comment after XML declaration
            comment = '\n<!-- MODERNIZED by SpringLift v2.1.1 - Updated to Java 21 and Spring Boot 3.x -->\n'
            content = content.replace('?>\n', '?>' + comment, 1)
            
            with open(pom_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            logger.info(f"Added modernization comment to {pom_path}")
            return True
        except Exception as e:
            logger.error(f"Error adding comment to pom.xml: {str(e)}")
            return False

    def get_pom_info(self, pom_path: str) -> Dict:
        """Extract key information from pom.xml"""
        info = {
            'project_name': None,
            'current_java_version': None,
            'current_spring_boot_version': None,
            'dependencies': []
        }
        
        try:
            with open(pom_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Extract project name
            match = re.search(r'<artifactId>(.*?)</artifactId>', content)
            if match:
                info['project_name'] = match.group(1)
            
            # Extract Java version
            match = re.search(r'<java\.version>(.*?)</java\.version>', content)
            if match:
                info['current_java_version'] = match.group(1)
            else:
                match = re.search(r'<maven\.compiler\.source>(.*?)</maven\.compiler\.source>', content)
                if match:
                    info['current_java_version'] = match.group(1)
            
            # Extract Spring Boot version
            match = re.search(r'<spring-boot\.version>(.*?)</spring-boot\.version>', content)
            if match:
                info['current_spring_boot_version'] = match.group(1)
            else:
                match = re.search(r'<version>(\d+\.\d+\.\d+)</version>\s*\n\s*</parent>', content)
                if match:
                    info['current_spring_boot_version'] = match.group(1)
            
            # Extract dependencies
            dep_pattern = r'<artifactId>(.*?)</artifactId>\s*<version>(.*?)</version>'
            for match in re.finditer(dep_pattern, content):
                info['dependencies'].append({
                    'name': match.group(1),
                    'version': match.group(2)
                })
            
            return info
        except Exception as e:
            logger.error(f"Error reading pom.xml info: {str(e)}")
            return info


# Global instance
pom_updater = PomUpdater()
