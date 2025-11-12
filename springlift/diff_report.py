"""
Diff Report Generator
Creates detailed before/after code comparison reports
"""
import difflib
from typing import Dict, List, Tuple
from .logger import logger
import json


class DiffReportGenerator:
    """
    Generates detailed diff reports showing code changes during modernization
    """
    
    @staticmethod
    def generate_file_diff(original_content: str, modernized_content: str, filename: str) -> Dict:
        """
        Generate a detailed diff between original and modernized code
        
        Returns: Dict with diff statistics and details
        """
        
        original_lines = original_content.splitlines(keepends=True)
        modernized_lines = modernized_content.splitlines(keepends=True)
        
        # Generate unified diff
        diff = list(difflib.unified_diff(
            original_lines,
            modernized_lines,
            fromfile=f"original/{filename}",
            tofile=f"modernized/{filename}",
            lineterm=''
        ))
        
        # Calculate statistics
        added_lines = sum(1 for line in diff if line.startswith('+') and not line.startswith('+++'))
        removed_lines = sum(1 for line in diff if line.startswith('-') and not line.startswith('---'))
        
        # Extract changed sections
        changed_sections = DiffReportGenerator._extract_changed_sections(
            original_lines, 
            modernized_lines, 
            filename
        )
        
        return {
            "filename": filename,
            "original_lines": len(original_lines),
            "modernized_lines": len(modernized_lines),
            "added_lines": added_lines,
            "removed_lines": removed_lines,
            "changed_lines": added_lines + removed_lines,
            "diff_ratio": DiffReportGenerator._calculate_diff_ratio(original_content, modernized_content),
            "unified_diff": ''.join(diff),
            "changed_sections": changed_sections,
        }
    
    @staticmethod
    def _extract_changed_sections(original_lines: List[str], modernized_lines: List[str], filename: str) -> List[Dict]:
        """
        Extract individual changed sections from the diff
        """
        sections = []
        
        matcher = difflib.SequenceMatcher(None, original_lines, modernized_lines)
        
        for tag, i1, i2, j1, j2 in matcher.get_opcodes():
            if tag != 'equal':
                section = {
                    "type": tag,  # 'replace', 'insert', 'delete'
                    "original_start": i1 + 1,
                    "original_end": i2,
                    "modernized_start": j1 + 1,
                    "modernized_end": j2,
                    "original_code": ''.join(original_lines[i1:i2]).strip(),
                    "modernized_code": ''.join(modernized_lines[j1:j2]).strip(),
                    "change_type": DiffReportGenerator._categorize_change(
                        ''.join(original_lines[i1:i2]),
                        ''.join(modernized_lines[j1:j2])
                    )
                }
                
                if section["original_code"] or section["modernized_code"]:
                    sections.append(section)
        
        return sections
    
    @staticmethod
    def _calculate_diff_ratio(original: str, modernized: str) -> float:
        """
        Calculate similarity ratio between original and modernized code
        """
        matcher = difflib.SequenceMatcher(None, original, modernized)
        return round(matcher.ratio() * 100, 2)
    
    @staticmethod
    def _categorize_change(original_code: str, modernized_code: str) -> str:
        """
        Categorize the type of change made
        """
        
        # javax to jakarta migration
        if 'javax.' in original_code and 'jakarta.' in modernized_code:
            return "namespace_migration"
        
        # Import additions
        if 'import' in modernized_code and 'import' not in original_code:
            return "import_added"
        
        # Import removals
        if 'import' in original_code and 'import' not in modernized_code:
            return "import_removed"
        
        # Comment additions
        if '//' in modernized_code and '//' not in original_code:
            return "comment_added"
        
        # Deprecated API removal
        if 'Deprecated' in original_code or '@Deprecated' in original_code:
            return "deprecated_removed"
        
        # Generic replacement
        return "code_updated"
    
    @staticmethod
    def generate_project_diff_report(file_diffs: List[Dict]) -> Dict:
        """
        Generate an overall project-level diff report
        
        Returns: Comprehensive report with statistics
        """
        
        total_files = len(file_diffs)
        
        # Calculate totals
        total_original_lines = sum(d.get("original_lines", 0) for d in file_diffs)
        total_modernized_lines = sum(d.get("modernized_lines", 0) for d in file_diffs)
        total_added_lines = sum(d.get("added_lines", 0) for d in file_diffs)
        total_removed_lines = sum(d.get("removed_lines", 0) for d in file_diffs)
        total_changed_lines = total_added_lines + total_removed_lines
        
        # Categorize changes
        change_categories = {}
        for file_diff in file_diffs:
            for section in file_diff.get("changed_sections", []):
                change_type = section.get("change_type", "unknown")
                change_categories[change_type] = change_categories.get(change_type, 0) + 1
        
        # Find most modified files
        most_modified = sorted(file_diffs, key=lambda x: x.get("changed_lines", 0), reverse=True)[:5]
        
        return {
            "summary": {
                "total_files_analyzed": total_files,
                "total_files_modified": sum(1 for d in file_diffs if d.get("changed_lines", 0) > 0),
                "total_original_lines": total_original_lines,
                "total_modernized_lines": total_modernized_lines,
                "total_lines_added": total_added_lines,
                "total_lines_removed": total_removed_lines,
                "total_lines_changed": total_changed_lines,
                "average_diff_ratio": round(
                    sum(d.get("diff_ratio", 100) for d in file_diffs) / max(1, total_files), 
                    2
                )
            },
            "change_categories": change_categories,
            "most_modified_files": [
                {
                    "filename": f.get("filename"),
                    "lines_changed": f.get("changed_lines", 0),
                    "added": f.get("added_lines", 0),
                    "removed": f.get("removed_lines", 0)
                }
                for f in most_modified
            ],
            "files": file_diffs
        }
    
    @staticmethod
    def generate_side_by_side_view(original_code: str, modernized_code: str, context_lines: int = 3) -> str:
        """
        Generate HTML side-by-side comparison view
        """
        
        html = """
        <table style="width:100%; border-collapse: collapse; font-family: monospace;">
            <tr style="background-color: #f0f0f0;">
                <th style="width: 50%; padding: 10px; border: 1px solid #ddd;">Original</th>
                <th style="width: 50%; padding: 10px; border: 1px solid #ddd;">Modernized</th>
            </tr>
        """
        
        original_lines = original_code.splitlines()
        modernized_lines = modernized_code.splitlines()
        
        matcher = difflib.SequenceMatcher(None, original_lines, modernized_lines)
        
        for tag, i1, i2, j1, j2 in matcher.get_opcodes():
            if tag == 'equal':
                # Show equal lines
                for i in range(i2 - i1):
                    line = original_lines[i1 + i]
                    html += f"""
                    <tr>
                        <td style="padding: 5px; border: 1px solid #ddd; background-color: #fff;">{DiffReportGenerator._escape_html(line)}</td>
                        <td style="padding: 5px; border: 1px solid #ddd; background-color: #fff;">{DiffReportGenerator._escape_html(line)}</td>
                    </tr>
                    """
            
            elif tag == 'delete':
                # Show removed lines
                for i in range(i2 - i1):
                    line = original_lines[i1 + i]
                    html += f"""
                    <tr>
                        <td style="padding: 5px; border: 1px solid #ddd; background-color: #ffcccc;">{DiffReportGenerator._escape_html(line)}</td>
                        <td style="padding: 5px; border: 1px solid #ddd; background-color: #fff;"></td>
                    </tr>
                    """
            
            elif tag == 'insert':
                # Show added lines
                for j in range(j2 - j1):
                    line = modernized_lines[j1 + j]
                    html += f"""
                    <tr>
                        <td style="padding: 5px; border: 1px solid #ddd; background-color: #fff;"></td>
                        <td style="padding: 5px; border: 1px solid #ddd; background-color: #ccffcc;">{DiffReportGenerator._escape_html(line)}</td>
                    </tr>
                    """
            
            elif tag == 'replace':
                # Show replaced lines
                for i, j in zip(range(i1, i2), range(j1, j2)):
                    orig_line = original_lines[i] if i < len(original_lines) else ""
                    mod_line = modernized_lines[j] if j < len(modernized_lines) else ""
                    html += f"""
                    <tr>
                        <td style="padding: 5px; border: 1px solid #ddd; background-color: #ffeecc;">{DiffReportGenerator._escape_html(orig_line)}</td>
                        <td style="padding: 5px; border: 1px solid #ddd; background-color: #eeffcc;">{DiffReportGenerator._escape_html(mod_line)}</td>
                    </tr>
                    """
                
                # Handle extra lines if replacement has different number of lines
                if i2 - i1 > j2 - j1:
                    for i in range(j2 - j1, i2 - i1):
                        line = original_lines[i1 + i]
                        html += f"""
                        <tr>
                            <td style="padding: 5px; border: 1px solid #ddd; background-color: #ffeecc;">{DiffReportGenerator._escape_html(line)}</td>
                            <td style="padding: 5px; border: 1px solid #ddd; background-color: #fff;"></td>
                        </tr>
                        """
                elif j2 - j1 > i2 - i1:
                    for j in range(i2 - i1, j2 - j1):
                        line = modernized_lines[j1 + j]
                        html += f"""
                        <tr>
                            <td style="padding: 5px; border: 1px solid #ddd; background-color: #fff;"></td>
                            <td style="padding: 5px; border: 1px solid #ddd; background-color: #eeffcc;">{DiffReportGenerator._escape_html(line)}</td>
                        </tr>
                        """
        
        html += "</table>"
        return html
    
    @staticmethod
    def _escape_html(text: str) -> str:
        """Escape HTML special characters"""
        text = text.replace("&", "&amp;")
        text = text.replace("<", "&lt;")
        text = text.replace(">", "&gt;")
        text = text.replace('"', "&quot;")
        text = text.replace("'", "&#39;")
        return text
    
    @staticmethod
    def export_diff_report_json(report: Dict, output_path: str) -> bool:
        """
        Export diff report as JSON file
        """
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(report, f, indent=2)
            logger.info(f"Diff report exported to {output_path}")
            return True
        except Exception as e:
            logger.error(f"Failed to export diff report: {str(e)}")
            return False


# Singleton instance
diff_report_generator = DiffReportGenerator()
