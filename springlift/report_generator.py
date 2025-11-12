"""
HTML Report Generator
Generates beautiful HTML reports for modernization analysis
"""
import os
from typing import Dict, List
from datetime import datetime
from .logger import logger


class HTMLReportGenerator:
    """
    Generates comprehensive HTML reports for modernization analysis
    """
    
    @staticmethod
    def generate_full_report(result: Dict, output_dir: str) -> bool:
        """
        Generate a complete HTML report
        
        Returns: True if successful
        """
        try:
            # Create output directory if it doesn't exist
            os.makedirs(output_dir, exist_ok=True)
            
            # Generate main report
            html_content = HTMLReportGenerator._generate_main_html(result)
            
            # Write report
            report_path = os.path.join(output_dir, "modernization_report.html")
            with open(report_path, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            logger.info(f"HTML report generated at {report_path}")
            return True
        
        except Exception as e:
            logger.error(f"Failed to generate HTML report: {str(e)}")
            return False
    
    @staticmethod
    def _generate_main_html(result: Dict) -> str:
        """
        Generate the main HTML report content
        """
        
        project_analysis = result.get('project_analysis', {})
        scan_id = result.get('id', 'N/A')
        created_at = result.get('created_at', 'N/A')
        output_path = result.get('output_path', 'N/A')
        
        html = f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>SpringLift - Java Modernization Report</title>
            <style>
                * {{
                    margin: 0;
                    padding: 0;
                    box-sizing: border-box;
                }}
                
                body {{
                    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    min-height: 100vh;
                    padding: 20px;
                }}
                
                .container {{
                    max-width: 1200px;
                    margin: 0 auto;
                    background: white;
                    border-radius: 10px;
                    box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);
                    overflow: hidden;
                }}
                
                .header {{
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    color: white;
                    padding: 40px 30px;
                    text-align: center;
                }}
                
                .header h1 {{
                    font-size: 32px;
                    margin-bottom: 10px;
                }}
                
                .header p {{
                    font-size: 16px;
                    opacity: 0.9;
                }}
                
                .content {{
                    padding: 30px;
                }}
                
                .section {{
                    margin-bottom: 30px;
                    border-bottom: 2px solid #eee;
                    padding-bottom: 20px;
                }}
                
                .section:last-child {{
                    border-bottom: none;
                }}
                
                .section h2 {{
                    font-size: 24px;
                    color: #333;
                    margin-bottom: 15px;
                    display: flex;
                    align-items: center;
                }}
                
                .section h2:before {{
                    content: '';
                    display: inline-block;
                    width: 4px;
                    height: 24px;
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    margin-right: 10px;
                }}
                
                .stats-grid {{
                    display: grid;
                    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                    gap: 20px;
                    margin: 20px 0;
                }}
                
                .stat-card {{
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    color: white;
                    padding: 20px;
                    border-radius: 8px;
                    text-align: center;
                }}
                
                .stat-card h3 {{
                    font-size: 12px;
                    text-transform: uppercase;
                    letter-spacing: 1px;
                    opacity: 0.9;
                    margin-bottom: 10px;
                }}
                
                .stat-card .number {{
                    font-size: 28px;
                    font-weight: bold;
                }}
                
                .file-table {{
                    width: 100%;
                    border-collapse: collapse;
                    margin: 20px 0;
                }}
                
                .file-table thead {{
                    background: #f5f5f5;
                }}
                
                .file-table th {{
                    padding: 12px;
                    text-align: left;
                    font-weight: 600;
                    color: #333;
                    border-bottom: 2px solid #ddd;
                }}
                
                .file-table td {{
                    padding: 12px;
                    border-bottom: 1px solid #eee;
                }}
                
                .file-table tr:hover {{
                    background: #f9f9f9;
                }}
                
                .issue-list {{
                    list-style: none;
                    margin: 15px 0;
                }}
                
                .issue-item {{
                    background: #fff3cd;
                    border-left: 4px solid #ffc107;
                    padding: 15px;
                    margin-bottom: 10px;
                    border-radius: 4px;
                }}
                
                .issue-item.error {{
                    background: #f8d7da;
                    border-left-color: #dc3545;
                }}
                
                .issue-item.success {{
                    background: #d4edda;
                    border-left-color: #28a745;
                }}
                
                .timestamp {{
                    color: #666;
                    font-size: 14px;
                    margin-top: 20px;
                    padding-top: 20px;
                    border-top: 1px solid #eee;
                    text-align: center;
                }}
                
                .badge {{
                    display: inline-block;
                    padding: 4px 8px;
                    border-radius: 4px;
                    font-size: 12px;
                    font-weight: 600;
                }}
                
                .badge-warning {{
                    background: #fff3cd;
                    color: #856404;
                }}
                
                .badge-success {{
                    background: #d4edda;
                    color: #155724;
                }}
                
                .badge-danger {{
                    background: #f8d7da;
                    color: #721c24;
                }}
                
                .progress-bar {{
                    width: 100%;
                    height: 8px;
                    background: #eee;
                    border-radius: 4px;
                    overflow: hidden;
                    margin: 10px 0;
                }}
                
                .progress-fill {{
                    height: 100%;
                    background: linear-gradient(90deg, #28a745 0%, #20c997 100%);
                    transition: width 0.3s ease;
                }}
                
                @media (max-width: 768px) {{
                    .header h1 {{
                        font-size: 24px;
                    }}
                    
                    .stats-grid {{
                        grid-template-columns: 1fr;
                    }}
                    
                    .file-table {{
                        font-size: 12px;
                    }}
                    
                    .file-table th, .file-table td {{
                        padding: 8px;
                    }}
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>SpringLift Modernization Report</h1>
                    <p>Automated Java 8/11 + Spring Boot 2.x → Java 21 + Spring Boot 3.x Migration</p>
                </div>
                
                <div class="content">
                    {HTMLReportGenerator._generate_summary_section(project_analysis, scan_id, created_at, output_path)}
                    {HTMLReportGenerator._generate_statistics_section(project_analysis)}
                    {HTMLReportGenerator._generate_files_section(project_analysis)}
                    {HTMLReportGenerator._generate_recommendations_section(project_analysis)}
                    {HTMLReportGenerator._generate_dependencies_section(project_analysis)}
                    {HTMLReportGenerator._generate_next_steps_section()}
                    
                    <div class="timestamp">
                        <p>Report generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
                        <p style="color: #999; font-size: 12px;">SpringLift v2.0.0 - Java Modernization Platform</p>
                    </div>
                </div>
            </div>
        </body>
        </html>
        """
        
        return html
    
    @staticmethod
    def _generate_summary_section(project_analysis: Dict, scan_id: str, created_at: str, output_path: str) -> str:
        """Generate summary section"""
        
        html = f"""
        <div class="section">
            <h2>Scan Summary</h2>
            <table style="width: 100%; border-collapse: collapse;">
                <tr>
                    <td style="padding: 8px; width: 200px; font-weight: 600;">Scan ID:</td>
                    <td style="padding: 8px; color: #667eea; font-family: monospace;">{scan_id}</td>
                </tr>
                <tr style="background: #f9f9f9;">
                    <td style="padding: 8px; font-weight: 600;">Created At:</td>
                    <td style="padding: 8px;">{created_at}</td>
                </tr>
                <tr>
                    <td style="padding: 8px; font-weight: 600;">Output Location:</td>
                    <td style="padding: 8px; font-family: monospace; color: #666;">{output_path}</td>
                </tr>
            </table>
        </div>
        """
        
        return html
    
    @staticmethod
    def _generate_statistics_section(project_analysis: Dict) -> str:
        """Generate statistics section"""
        
        total_files = project_analysis.get('total_files_analyzed', 0)
        issues_found = project_analysis.get('issues_found', 0)
        transformations = project_analysis.get('total_transformations', 0)
        
        success_rate = round((total_files - issues_found) / max(1, total_files) * 100, 1) if total_files > 0 else 0
        
        html = f"""
        <div class="section">
            <h2>Analysis Statistics</h2>
            <div class="stats-grid">
                <div class="stat-card">
                    <h3>Files Analyzed</h3>
                    <div class="number">{total_files}</div>
                </div>
                <div class="stat-card">
                    <h3>Issues Found</h3>
                    <div class="number">{issues_found}</div>
                </div>
                <div class="stat-card">
                    <h3>Transformations Applied</h3>
                    <div class="number">{transformations}</div>
                </div>
                <div class="stat-card">
                    <h3>Success Rate</h3>
                    <div class="number">{success_rate}%</div>
                </div>
            </div>
        </div>
        """
        
        return html
    
    @staticmethod
    def _generate_files_section(project_analysis: Dict) -> str:
        """Generate files analysis section"""
        
        file_analyses = project_analysis.get('file_analyses', [])
        
        if not file_analyses:
            return """
            <div class="section">
                <h2>File Analysis</h2>
                <p style="color: #666;">No files analyzed.</p>
            </div>
            """
        
        html = """
        <div class="section">
            <h2>File Analysis</h2>
            <table class="file-table">
                <thead>
                    <tr>
                        <th>Filename</th>
                        <th>Issues Found</th>
                        <th>Suggestions</th>
                        <th>Transformations</th>
                    </tr>
                </thead>
                <tbody>
        """
        
        for file_analysis in file_analyses[:10]:  # Show first 10 files
            filename = file_analysis.get('filename', 'N/A')
            issues_count = len(file_analysis.get('issues', []))
            suggestions_count = len(file_analysis.get('suggestions', []))
            transformations_count = len(file_analysis.get('transformations', {}))
            
            html += f"""
                    <tr>
                        <td style="font-family: monospace; color: #667eea;">{filename}</td>
                        <td><span class="badge badge-danger">{issues_count}</span></td>
                        <td><span class="badge badge-warning">{suggestions_count}</span></td>
                        <td><span class="badge badge-success">{transformations_count}</span></td>
                    </tr>
            """
        
        if len(file_analyses) > 10:
            html += f"""
                    <tr>
                        <td colspan="4" style="text-align: center; padding: 15px; color: #666;">
                            ... and {len(file_analyses) - 10} more files
                        </td>
                    </tr>
            """
        
        html += """
                </tbody>
            </table>
        </div>
        """
        
        return html
    
    @staticmethod
    def _generate_recommendations_section(project_analysis: Dict) -> str:
        """Generate recommendations section"""
        
        build_recommendations = project_analysis.get('build_recommendations', [])
        
        if not build_recommendations:
            return ""
        
        html = """
        <div class="section">
            <h2>Key Recommendations</h2>
            <ul class="issue-list">
        """
        
        for recommendation in build_recommendations[:5]:  # Show first 5
            html += f'<li class="issue-item success">✓ {recommendation}</li>'
        
        if len(build_recommendations) > 5:
            html += f'<li class="issue-item" style="background: #e7f3ff; border-left-color: #2196F3;">... and {len(build_recommendations) - 5} more recommendations</li>'
        
        html += """
            </ul>
        </div>
        """
        
        return html
    
    @staticmethod
    def _generate_dependencies_section(project_analysis: Dict) -> str:
        """Generate dependencies section"""
        
        dependency_upgrades = project_analysis.get('dependency_upgrades', {})
        dependency_issues = project_analysis.get('dependency_issues', [])
        
        if not dependency_upgrades and not dependency_issues:
            return ""
        
        html = """
        <div class="section">
            <h2>Dependency Analysis</h2>
        """
        
        if dependency_issues:
            html += """
            <h3>Issues Found</h3>
            <ul class="issue-list">
            """
            
            for issue in dependency_issues[:5]:
                html += f'<li class="issue-item error">⚠️ {issue}</li>'
            
            html += "</ul>"
        
        if dependency_upgrades:
            html += """
            <h3>Recommended Upgrades</h3>
            <table class="file-table">
                <thead>
                    <tr>
                        <th>Dependency</th>
                        <th>Recommended Version</th>
                    </tr>
                </thead>
                <tbody>
            """
            
            for dep, version in list(dependency_upgrades.items())[:10]:
                html += f"""
                    <tr>
                        <td style="font-family: monospace;">{dep}</td>
                        <td><span class="badge badge-success">{version}</span></td>
                    </tr>
                """
            
            html += """
                </tbody>
            </table>
            """
        
        html += "</div>"
        
        return html
    
    @staticmethod
    def _generate_next_steps_section() -> str:
        """Generate next steps section"""
        
        html = """
        <div class="section">
            <h2>Next Steps</h2>
            <ol style="line-height: 1.8; margin-left: 20px;">
                <li><strong>Review the Modernized Code:</strong> Navigate to the output directory and examine the transformed Java files</li>
                <li><strong>Check Dependency Updates:</strong> Update your pom.xml or build.gradle with recommended version upgrades</li>
                <li><strong>Run Tests:</strong> Execute your test suite to ensure compatibility with modernized code</li>
                <li><strong>Manual Review:</strong> Review any AI-generated suggestions and apply as needed</li>
                <li><strong>Update Configuration:</strong> Migrate any configuration files (application.yml, application.properties)</li>
                <li><strong>Deploy & Test:</strong> Test in staging environment before production deployment</li>
            </ol>
        </div>
        """
        
        return html


# Singleton instance
html_report_generator = HTMLReportGenerator()
