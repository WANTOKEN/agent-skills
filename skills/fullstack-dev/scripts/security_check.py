#!/usr/bin/env python3
"""
Security Self-Check Script for Full-Stack Projects
Automatically detects and reports common security issues
"""

import os
import re
import json
from pathlib import Path
from typing import List, Dict, Any

class SecurityChecker:
    """Automated security vulnerability scanner"""
    
    def __init__(self, project_root: str):
        self.root = Path(project_root)
        self.issues: List[Dict[str, Any]] = []
        self.warnings: List[Dict[str, Any]] = []
        
    def check_all(self) -> Dict[str, Any]:
        """Run all security checks"""
        self.check_hardcoded_secrets()
        self.check_database_urls()
        self.check_env_files()
        self.check_dependency_vulnerabilities()
        self.check_sql_injection_patterns()
        self.check_xss_patterns()
        
        return {
            "issues": self.issues,
            "warnings": self.warnings,
            "passed": len(self.issues) == 0,
            "summary": {
                "critical": len([i for i in self.issues if i["severity"] == "critical"]),
                "warning": len([i for i in self.issues if i["severity"] == "warning"]),
                "info": len(self.warnings)
            }
        }
    
    def check_hardcoded_secrets(self) -> None:
        """Detect hardcoded secrets and API keys"""
        secret_patterns = [
            (r'password\s*=\s*["\'](?!\$\{)[^"\']+["\']', "Hardcoded password"),
            (r'secret_key\s*=\s*["\'](?!\$\{)[^"\']+["\']', "Hardcoded secret key"),
            (r'api_key\s*=\s*["\'](?!\$\{)[^"\']+["\']', "Hardcoded API key"),
            (r'aws_access_key_id\s*=\s*["\']AK[A-Z0-9]{16}["\']', "AWS access key"),
            (r'aws_secret_access_key\s*=\s*["\'][A-Za-z0-9/+=]{40}["\']', "AWS secret key"),
        ]
        
        for file_path in self._get_source_files():
            content = file_path.read_text(encoding='utf-8', errors='ignore')
            for pattern, message in secret_patterns:
                matches = re.finditer(pattern, content, re.IGNORECASE)
                for match in matches:
                    line_num = content[:match.start()].count('\n') + 1
                    self.issues.append({
                        "file": str(file_path.relative_to(self.root)),
                        "line": line_num,
                        "type": "hardcoded_secret",
                        "severity": "critical",
                        "message": message,
                        "code": match.group(0)[:50] + "..." if len(match.group(0)) > 50 else match.group(0)
                    })
    
    def check_database_urls(self) -> None:
        """Detect exposed database connection strings"""
        db_url_patterns = [
            r'postgresql://[^:]+:[^@]+@[^/]+/\w+',
            r'mysql://[^:]+:[^@]+@[^/]+/\w+',
            r'mongodb://[^:]+:[^@]+@[^/]+/\w+',
            r'redis://[^:]+:[^@]+@[^/]+/\d+',
        ]
        
        for file_path in self._get_source_files():
            content = file_path.read_text(encoding='utf-8', errors='ignore')
            for pattern in db_url_patterns:
                matches = re.finditer(pattern, content)
                for match in matches:
                    # Skip if it uses environment variable placeholder
                    if '${' in match.group(0) or '***' in match.group(0):
                        continue
                    line_num = content[:match.start()].count('\n') + 1
                    self.issues.append({
                        "file": str(file_path.relative_to(self.root)),
                        "line": line_num,
                        "type": "exposed_db_url",
                        "severity": "critical",
                        "message": "Database connection string with credentials exposed",
                        "code": self._mask_credentials(match.group(0))
                    })
    
    def check_env_files(self) -> None:
        """Check for .env file issues"""
        # Check if .env is tracked by git
        gitignore = self.root / '.gitignore'
        if gitignore.exists():
            gitignore_content = gitignore.read_text()
            if '.env' not in gitignore_content:
                self.warnings.append({
                    "type": "gitignore",
                    "message": ".env not in .gitignore - may accidentally commit secrets"
                })
        
        # Check for example env file
        if not (self.root / '.env.example').exists():
            self.warnings.append({
                "type": "env_example",
                "message": "No .env.example file found - create one for documentation"
            })
    
    def check_dependency_vulnerabilities(self) -> None:
        """Check for known vulnerable dependencies"""
        # Check package.json
        package_json = self.root / 'package.json'
        if package_json.exists():
            self.warnings.append({
                "type": "npm_audit",
                "message": "Run 'npm audit' to check for vulnerable dependencies"
            })
        
        # Check requirements.txt
        requirements = self.root / 'requirements.txt'
        if requirements.exists():
            self.warnings.append({
                "type": "pip_audit",
                "message": "Run 'pip-audit' to check for vulnerable dependencies"
            })
    
    def check_sql_injection_patterns(self) -> None:
        """Detect potential SQL injection vulnerabilities"""
        sql_patterns = [
            (r'f["\'].*SELECT.*\{[^}]+\}.*["\']', "f-string in SQL query"),
            (r'\.execute\(f["\']', "f-string in execute()"),
            (r'\.executemany\(f["\']', "f-string in executemany()"),
        ]
        
        for file_path in self._get_source_files(['.py']):
            content = file_path.read_text(encoding='utf-8', errors='ignore')
            for pattern, message in sql_patterns:
                matches = re.finditer(pattern, content, re.IGNORECASE)
                for match in matches:
                    line_num = content[:match.start()].count('\n') + 1
                    self.issues.append({
                        "file": str(file_path.relative_to(self.root)),
                        "line": line_num,
                        "type": "sql_injection",
                        "severity": "critical",
                        "message": f"Potential SQL injection: {message}",
                        "code": match.group(0)
                    })
    
    def check_xss_patterns(self) -> None:
        """Detect potential XSS vulnerabilities"""
        xss_patterns = [
            (r'dangerouslySetInnerHTML.*\{[^}]*\}', "dangerouslySetInnerHTML usage"),
            (r'innerHTML\s*=', "innerHTML assignment"),
            (r'document\.write\(', "document.write usage"),
        ]
        
        for file_path in self._get_source_files(['.js', '.jsx', '.ts', '.tsx']):
            content = file_path.read_text(encoding='utf-8', errors='ignore')
            for pattern, message in xss_patterns:
                matches = re.finditer(pattern, content)
                for match in matches:
                    line_num = content[:match.start()].count('\n') + 1
                    self.warnings.append({
                        "file": str(file_path.relative_to(self.root)),
                        "line": line_num,
                        "type": "xss_potential",
                        "message": f"Potential XSS: {message} - ensure content is sanitized",
                        "code": match.group(0)[:50]
                    })
    
    def _get_source_files(self, extensions: List[str] = None) -> List[Path]:
        """Get all source files in project"""
        if extensions is None:
            extensions = ['.py', '.js', '.jsx', '.ts', '.tsx', '.env', '.yaml', '.yml']
        
        files = []
        for ext in extensions:
            files.extend(self.root.rglob(f'*{ext}'))
        
        # Exclude common non-source directories
        exclude_dirs = {'node_modules', '.git', '__pycache__', 'venv', '.venv', 'dist', 'build'}
        return [f for f in files if not any(d in f.parts for d in exclude_dirs)]
    
    def _mask_credentials(self, url: str) -> str:
        """Mask credentials in URL for safe reporting"""
        return re.sub(r'://([^:]+):([^@]+)@', r'://\1:***@', url)


def generate_fix_suggestions(results: Dict[str, Any]) -> str:
    """Generate fix suggestions for detected issues"""
    suggestions = []
    
    for issue in results["issues"]:
        if issue["type"] == "hardcoded_secret":
            suggestions.append(f"""
# Fix for {issue['file']}:{issue['line']}
# Replace hardcoded value with environment variable:
# Before: {issue['code']}
# After:  SECRET_KEY = os.environ.get('SECRET_KEY')
""")
        elif issue["type"] == "exposed_db_url":
            suggestions.append(f"""
# Fix for {issue['file']}:{issue['line']}
# Use environment variable for database URL:
# Before: {issue['code']}
# After:  DATABASE_URL = os.environ.get('DATABASE_URL')
""")
        elif issue["type"] == "sql_injection":
            suggestions.append(f"""
# Fix for {issue['file']}:{issue['line']}
# Use parameterized queries:
# Before: {issue['code']}
# After:  cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))
""")
    
    return "\n".join(suggestions)


def main():
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python security_check.py <project_directory>")
        sys.exit(1)
    
    project_root = sys.argv[1]
    checker = SecurityChecker(project_root)
    results = checker.check_all()
    
    # Print report
    print("\n" + "="*60)
    print("🔒 SECURITY CHECK REPORT")
    print("="*60)
    
    if results["passed"]:
        print("\n✅ No critical security issues found!")
    else:
        print(f"\n❌ Found {len(results['issues'])} security issue(s)")
        
        for issue in results["issues"]:
            severity_icon = "🚨" if issue["severity"] == "critical" else "⚠️"
            print(f"\n{severity_icon} [{issue['severity'].upper()}] {issue['type']}")
            print(f"   File: {issue['file']}:{issue['line']}")
            print(f"   Message: {issue['message']}")
            print(f"   Code: {issue['code']}")
    
    if results["warnings"]:
        print(f"\n⚠️  {len(results['warnings'])} warning(s):")
        for warning in results["warnings"]:
            print(f"   - {warning['message']}")
    
    print("\n" + "="*60)
    print(f"Summary: {results['summary']['critical']} critical, "
          f"{results['summary']['warning']} warnings, "
          f"{results['summary']['info']} info")
    print("="*60 + "\n")
    
    # Generate fix suggestions
    if not results["passed"]:
        print("📝 FIX SUGGESTIONS:")
        print(generate_fix_suggestions(results))
    
    # Output JSON for CI/CD integration
    with open("security_report.json", "w") as f:
        json.dump(results, f, indent=2)
    print("\n📄 Full report saved to security_report.json")
    
    sys.exit(0 if results["passed"] else 1)


if __name__ == "__main__":
    main()
