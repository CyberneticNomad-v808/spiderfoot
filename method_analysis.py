#!/usr/bin/env python3
"""
Method-by-Method Analysis Script
Deep dive into function/method changes in key files
"""

import subprocess
import re
from datetime import datetime

def run_git_command(cmd):
    """Run a git command and return the output"""
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, cwd='/stuff/spiderfoot')
        return result.stdout.strip()
    except Exception as e:
        return f"Error: {e}"

def append_to_md(content, filename="branch_analysis.md"):
    """Append content to the markdown file"""
    with open(filename, 'a', encoding='utf-8') as f:
        f.write(content + '\n')

def extract_functions_and_methods(file_content):
    """Extract function and method definitions from Python code"""
    functions = []
    lines = file_content.split('\n')
    
    for i, line in enumerate(lines):
        # Match function/method definitions
        if re.match(r'^(class |def |    def )', line.strip()):
            # Get the full signature (handle multi-line definitions)
            signature = line.strip()
            j = i + 1
            while j < len(lines) and lines[j].strip().endswith((',', '\\')):
                signature += ' ' + lines[j].strip()
                j += 1
            
            functions.append({
                'line': i + 1,
                'signature': signature,
                'type': 'class' if signature.startswith('class') else 'method' if signature.startswith('    def') else 'function'
            })
    
    return functions

def analyze_file_methods(filename):
    """Analyze method changes in a specific file"""
    append_to_md(f"\n## Method-by-Method Analysis: {filename}")
    
    # Get current version functions
    current_content = run_git_command(f"cat {filename}")
    current_functions = extract_functions_and_methods(current_content) if current_content else []
    
    # Get dev-5.3.3 version functions
    dev_content = run_git_command(f"git show dev-5.3.3:{filename}")
    dev_functions = extract_functions_and_methods(dev_content) if dev_content and "Error:" not in dev_content else []
    
    # Create signature sets for comparison
    current_sigs = {f['signature'].split('(')[0].strip() for f in current_functions}
    dev_sigs = {f['signature'].split('(')[0].strip() for f in dev_functions}
    
    # Find new, removed, and common functions
    new_functions = current_sigs - dev_sigs
    removed_functions = dev_sigs - current_sigs
    common_functions = current_sigs & dev_sigs
    
    append_to_md(f"\n### Summary")
    append_to_md(f"- **Current version:** {len(current_functions)} functions/methods/classes")
    append_to_md(f"- **dev-5.3.3 version:** {len(dev_functions)} functions/methods/classes")
    append_to_md(f"- **New:** {len(new_functions)}")
    append_to_md(f"- **Removed:** {len(removed_functions)}")
    append_to_md(f"- **Common:** {len(common_functions)}")
    
    if new_functions:
        append_to_md(f"\n### ✅ New Functions/Methods ({len(new_functions)})")
        for func in sorted(new_functions):
            # Find full signature
            full_sig = next((f['signature'] for f in current_functions if f['signature'].startswith(func)), func)
            append_to_md(f"- `{full_sig}`")
    
    if removed_functions:
        append_to_md(f"\n### ❌ Removed Functions/Methods ({len(removed_functions)})")
        for func in sorted(removed_functions):
            # Find full signature
            full_sig = next((f['signature'] for f in dev_functions if f['signature'].startswith(func)), func)
            append_to_md(f"- `{full_sig}`")
    
    # Analyze line changes for common functions
    if common_functions:
        append_to_md(f"\n### 🔄 Modified Functions/Methods (showing line count changes)")
        for func_name in sorted(list(common_functions)[:10]):  # Limit to first 10
            # Get line counts (rough estimate)
            current_func = next((f for f in current_functions if f['signature'].startswith(func_name)), None)
            dev_func = next((f for f in dev_functions if f['signature'].startswith(func_name)), None)
            
            if current_func and dev_func:
                append_to_md(f"- `{func_name}` (line {current_func['line']} vs {dev_func['line']})")

def analyze_module_methods():
    """Analyze method changes in key modules"""
    append_to_md("\n---\n# Detailed Method Analysis")
    
    # Key files to analyze in detail
    key_files = [
        'sf.py',
        'sfapi.py', 
        'sfcli.py',
        'sfwebui.py',
        'sflib.py',
        'spiderfoot/db.py'
    ]
    
    for filename in key_files:
        try:
            analyze_file_methods(filename)
        except Exception as e:
            append_to_md(f"\n## Error analyzing {filename}: {e}")

def analyze_significant_module_changes():
    """Analyze modules with significant changes"""
    append_to_md("\n---\n# Significant Module Changes")
    
    # Get modules with significant line changes
    module_stats = run_git_command("git diff --stat dev-5.3.3 modules/ | grep '\\.py' | grep -E '[0-9]{2,}' | head -10")
    
    if module_stats:
        for line in module_stats.split('\n'):
            if line.strip() and '.py' in line:
                # Extract module name
                parts = line.strip().split()
                if parts:
                    module_name = parts[0]
                    append_to_md(f"\n## {module_name}")
                    
                    # Get function changes for this module
                    current_funcs = run_git_command(f"grep -n '^def ' {module_name} | head -5")
                    dev_funcs = run_git_command(f"git show dev-5.3.3:{module_name} | grep -n '^def ' | head -5")
                    
                    append_to_md(f"**Change summary:** {line.strip()}")
                    
                    if current_funcs:
                        append_to_md("**Current functions (first 5):**")
                        for func in current_funcs.split('\n'):
                            if func.strip():
                                append_to_md(f"- `{func.strip()}`")

def main():
    """Main execution"""
    print("Starting detailed method analysis...")
    
    append_to_md(f"\n---\n# DETAILED METHOD ANALYSIS\n**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    analyze_module_methods()
    analyze_significant_module_changes()
    
    print("Detailed analysis complete!")

if __name__ == "__main__":
    main()