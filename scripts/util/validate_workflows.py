#!/usr/bin/env python3
"""Validate workflow YAML files and PowerShell script syntax."""
import yaml
import subprocess
import tempfile
import os
from pathlib import Path


def validate_yaml(filepath: Path) -> tuple[bool, str]:
    """Validate YAML syntax."""
    try:
        with open(filepath, encoding='utf-8') as f:
            yaml.safe_load(f)
        return True, ""
    except yaml.YAMLError as e:
        return False, str(e)


def validate_powershell(script: str) -> tuple[bool, str]:
    """Validate PowerShell script syntax using pwsh parser.
    
    Note: GitHub Actions expressions like ${{ }} are replaced before execution,
    so we substitute them with dummy values for validation.
    """
    import re
    
    # Replace GitHub Actions expressions with dummy values
    # Be careful not to corrupt valid PowerShell syntax
    
    processed = script
    
    # Strategy: replace ${{ xxx }} with simple string "GHA_EXPR" 
    # This avoids complex regex that might match too much
    processed = re.sub(r'\$\{\{[^}]+\}\}', 'GHA_EXPR', processed)
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.ps1', delete=False, encoding='utf-8') as f:
        f.write(processed)
        temp_path = f.name
    
    try:
        # Use PowerShell parser to check syntax
        cmd = f'''
$errors = $null
[System.Management.Automation.Language.Parser]::ParseFile("{temp_path}", [ref]$null, [ref]$errors) | Out-Null
if ($errors.Count -gt 0) {{
    $errors | ForEach-Object {{ Write-Output $_.Message }}
    exit 1
}}
exit 0
'''
        result = subprocess.run(
            ['pwsh', '-NoProfile', '-Command', cmd],
            capture_output=True, text=True, timeout=10
        )
        if result.returncode != 0:
            return False, result.stdout or result.stderr
        return True, ""
    except subprocess.TimeoutExpired:
        return False, "Timeout validating script"
    except Exception as e:
        return False, str(e)
    finally:
        os.unlink(temp_path)


def main():
    workflows_dir = Path('.github/workflows')
    
    if not workflows_dir.exists():
        print("❌ .github/workflows directory not found")
        return 1
    
    all_valid = True
    
    for wf_file in workflows_dir.glob('*.yml'):
        print(f"\n📄 {wf_file.name}")
        
        # Validate YAML
        valid, error = validate_yaml(wf_file)
        if not valid:
            print(f"  ❌ YAML Error: {error}")
            all_valid = False
            continue
        print("  ✅ YAML syntax valid")
        
        # Load and find PowerShell scripts
        with open(wf_file, encoding='utf-8') as f:
            wf = yaml.safe_load(f)
        
        jobs = wf.get('jobs', {})
        for job_name, job in jobs.items():
            steps = job.get('steps', [])
            for i, step in enumerate(steps):
                shell = step.get('shell', '')
                run_script = step.get('run', '')
                
                if shell == 'pwsh' and run_script:
                    step_name = step.get('name', f'step-{i}')
                    valid, error = validate_powershell(run_script)
                    if valid:
                        print(f"  ✅ {job_name}/{step_name}: PowerShell OK")
                    else:
                        print(f"  ❌ {job_name}/{step_name}: {error}")
                        all_valid = False
    
    print("\n" + "="*50)
    if all_valid:
        print("✅ All workflows validated successfully!")
        return 0
    else:
        print("❌ Some validations failed")
        return 1


if __name__ == '__main__':
    exit(main())
