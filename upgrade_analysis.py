#!/usr/bin/env python3
"""
Correct SpiderFoot Upgrade Analysis
FROM: prod-_808_-5.2.9 (current simplified)
TO: dev-5.3.3 (advanced target)
Shows what needs to be added/removed/changed to upgrade
"""

import subprocess
import os
import re
from pathlib import Path
from datetime import datetime

def run_git_command(cmd):
    """Run a git command and return the output"""
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, cwd='/stuff/spiderfoot')
        return result.stdout.strip()
    except Exception as e:
        return f"Error: {e}"

def append_to_md(content, filename="upgrade_to_dev533.md"):
    """Append content to the markdown file"""
    with open(filename, 'a', encoding='utf-8') as f:
        f.write(content + '\n')

def initialize_md_file():
    """Initialize the upgrade analysis file"""
    filename = "upgrade_to_dev533.md"
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(f"""# SpiderFoot Upgrade Analysis: 5.2.9 → 5.3.3

**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**FROM:** prod-_808_-5.2.9 (current simplified branch)
**TO:** dev-5.3.3 (advanced modular target)

## Upgrade Path Analysis
This document shows what changes are needed to upgrade from the current simplified version to the advanced modular version.

---

""")
    return filename

def analyze_files_to_add():
    """Analyze files that need to be added (exist in dev-5.3.3 but not current)"""
    append_to_md("## 🟢 FILES TO ADD (exist in dev-5.3.3, missing in current)")
    
    # Get files that exist in dev-5.3.3 but not in current
    dev_files = run_git_command("git ls-tree -r --name-only dev-5.3.3")
    current_files = run_git_command("find . -type f -name '*.py' | sed 's|^./||'")
    
    if dev_files and current_files:
        dev_set = set(dev_files.split('\n'))
        current_set = set(current_files.split('\n'))
        
        # Files to add
        files_to_add = []
        for file in dev_set:
            if file not in current_set and not os.path.exists(file):
                files_to_add.append(file)
        
        # Group by directory
        dirs = {}
        for file in files_to_add[:50]:  # Limit output
            dir_name = '/'.join(file.split('/')[:-1]) if '/' in file else 'root'
            if dir_name not in dirs:
                dirs[dir_name] = []
            dirs[dir_name].append(file)
        
        for dir_name, files in sorted(dirs.items()):
            append_to_md(f"\n### {dir_name}/")
            for file in sorted(files):
                lines = run_git_command(f"git show dev-5.3.3:{file} | wc -l")
                append_to_md(f"- `{file}` ({lines} lines)")

def analyze_files_to_remove():
    """Analyze files that need to be removed (exist in current but not dev-5.3.3)"""
    append_to_md("\n## 🔴 FILES TO REMOVE (exist in current, not in dev-5.3.3)")
    
    # Get files in current that don't exist in dev-5.3.3
    diff_removed = run_git_command("git diff HEAD dev-5.3.3 --name-status | grep '^D' | cut -f2")
    
    if diff_removed:
        dirs = {}
        for file in diff_removed.split('\n')[:30]:
            if file.strip():
                dir_name = '/'.join(file.split('/')[:-1]) if '/' in file else 'root'
                if dir_name not in dirs:
                    dirs[dir_name] = []
                dirs[dir_name].append(file)
        
        for dir_name, files in sorted(dirs.items()):
            append_to_md(f"\n### {dir_name}/")
            for file in sorted(files):
                if os.path.exists(file):
                    lines = run_git_command(f"wc -l {file} | cut -d' ' -f1")
                    append_to_md(f"- `{file}` ({lines} lines) - **REMOVE**")

def analyze_modular_structure_to_add():
    """Analyze the modular structure that needs to be created"""
    append_to_md("\n## 🏗️ MODULAR ARCHITECTURE TO CREATE")
    
    modular_dirs = ['spiderfoot/api/', 'spiderfoot/cli/', 'spiderfoot/core/', 'spiderfoot/webui/', 'spiderfoot/db/']
    
    for dir_path in modular_dirs:
        append_to_md(f"\n### {dir_path}")
        
        # Get what needs to be created in this directory
        dir_contents = run_git_command(f"git ls-tree -r --name-only dev-5.3.3 | grep '^{dir_path}'")
        
        if dir_contents:
            append_to_md("**Modular components to create:**")
            total_lines = 0
            for file in dir_contents.split('\n'):
                if file.strip():
                    lines = run_git_command(f"git show dev-5.3.3:{file} | wc -l")
                    if lines.isdigit():
                        total_lines += int(lines)
                    append_to_md(f"- `{file}` ({lines} lines)")
            
            append_to_md(f"**Total for {dir_path}: {total_lines} lines of modular architecture**")

def analyze_file_decomposition():
    """Analyze how current monolithic files need to be decomposed"""
    append_to_md("\n## 🔀 FILE DECOMPOSITION NEEDED")
    
    main_files = ['sf.py', 'sfapi.py', 'sfcli.py', 'sfwebui.py']
    
    for file in main_files:
        if os.path.exists(file):
            append_to_md(f"\n### {file} - Needs Decomposition")
            
            # Current size
            current_lines = run_git_command(f"wc -l {file} | cut -d' ' -f1")
            
            # Target size in dev-5.3.3
            dev_lines = run_git_command(f"git show dev-5.3.3:{file} | wc -l")
            
            if current_lines.isdigit() and dev_lines.isdigit():
                reduction = int(current_lines) - int(dev_lines)
                append_to_md(f"- **Current (monolithic):** {current_lines} lines")
                append_to_md(f"- **Target (modular):** {dev_lines} lines")
                append_to_md(f"- **Needs extraction:** {reduction} lines to be moved to modular components")
                
                # Show current functions that need to be moved
                current_funcs = run_git_command(f"grep -n '^def \\|^class ' {file} | head -5")
                if current_funcs:
                    append_to_md("**Functions/classes to relocate:**")
                    for func in current_funcs.split('\n'):
                        if func.strip():
                            append_to_md(f"  - `{func.strip()}`")

def analyze_modules_to_add():
    """Analyze modules that need to be added"""
    append_to_md("\n## 📦 MODULES TO ADD")
    
    # Find modules in dev-5.3.3 that don't exist in current
    dev_modules = run_git_command("git ls-tree --name-only dev-5.3.3:modules/ | grep '\\.py$'")
    current_modules = run_git_command("ls modules/*.py 2>/dev/null | xargs -n1 basename")
    
    if dev_modules and current_modules:
        dev_set = set(dev_modules.split('\n'))
        current_set = set(current_modules.split('\n'))
        missing_modules = dev_set - current_set
        
        if missing_modules:
            append_to_md(f"\n**{len(missing_modules)} advanced modules to add:**")
            for module in sorted(missing_modules):
                if module.strip():
                    lines = run_git_command(f"git show dev-5.3.3:modules/{module} | wc -l")
                    append_to_md(f"- `modules/{module}` ({lines} lines) - **ADD**")

def analyze_upgrade_effort():
    """Calculate overall upgrade effort"""
    append_to_md("\n## 📊 UPGRADE EFFORT ANALYSIS")
    
    # Get total diff stats
    total_stats = run_git_command("git diff HEAD dev-5.3.3 --stat | tail -1")
    append_to_md(f"- **Total changes needed:** {total_stats}")
    
    # Count files to add vs remove
    files_added = run_git_command("git diff HEAD dev-5.3.3 --name-status | grep '^A' | wc -l")
    files_removed = run_git_command("git diff HEAD dev-5.3.3 --name-status | grep '^D' | wc -l")
    files_modified = run_git_command("git diff HEAD dev-5.3.3 --name-status | grep '^M' | wc -l")
    
    append_to_md(f"- **Files to add:** {files_added}")
    append_to_md(f"- **Files to remove:** {files_removed}")
    append_to_md(f"- **Files to modify:** {files_modified}")
    
    append_to_md("\n### Upgrade Roadmap:")
    append_to_md("1. **Create modular directory structure** (spiderfoot/api/, cli/, core/, webui/, db/)")
    append_to_md("2. **Decompose monolithic files** - extract functions into modular components")
    append_to_md("3. **Add missing enterprise modules** - advanced correlation, performance optimization")
    append_to_md("4. **Add testing infrastructure** - ThreadReaper framework and advanced testing")
    append_to_md("5. **Add security hardening** - enterprise security components")
    append_to_md("6. **Remove simplified consolidation files** - build scripts, deployment guides")
    
    append_to_md("\n### Complexity Assessment:")
    append_to_md("- **HIGH COMPLEXITY** - Major architectural refactoring required")
    append_to_md("- **BREAKING CHANGES** - API and CLI interfaces will change significantly")
    append_to_md("- **EXTENSIVE TESTING** - Advanced testing framework needs to be implemented")
    append_to_md("- **ENTERPRISE FEATURES** - Security and performance modules need integration")

def main():
    """Main execution"""
    os.chdir('/stuff/spiderfoot')
    
    print("Initializing upgrade analysis...")
    filename = initialize_md_file()
    
    print("Analyzing files to add...")
    analyze_files_to_add()
    
    print("Analyzing files to remove...")
    analyze_files_to_remove()
    
    print("Analyzing modular structure...")
    analyze_modular_structure_to_add()
    
    print("Analyzing file decomposition...")
    analyze_file_decomposition()
    
    print("Analyzing modules to add...")
    analyze_modules_to_add()
    
    print("Calculating upgrade effort...")
    analyze_upgrade_effort()
    
    print(f"\nUpgrade analysis complete! Results saved to: {filename}")
    print(f"File location: /stuff/spiderfoot/{filename}")

if __name__ == "__main__":
    main()