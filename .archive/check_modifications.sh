#!/bin/bash

# Check modification times and sizes of files that should have been fixed
# Output to markdown file for review

OUTPUT_FILE="/tmp/file_modification_audit.md"

echo "# File Modification Audit Report" > "$OUTPUT_FILE"
echo "Generated: $(date)" >> "$OUTPUT_FILE"
echo "" >> "$OUTPUT_FILE"

# List of key files that should have been modified by agents
FILES=(
    "/stuff/spiderfoot/spiderfoot/plugin.py"
    "/stuff/spiderfoot/spiderfoot/db.py"
    "/stuff/spiderfoot/spiderfoot/event.py"
    "/stuff/spiderfoot/spiderfoot/logger.py"
    "/stuff/spiderfoot/spiderfoot/helpers.py"
    "/stuff/spiderfoot/spiderfoot/target.py"
    "/stuff/spiderfoot/spiderfoot/__version__.py"
    "/stuff/spiderfoot/spiderfoot/threadpool.py"
    "/stuff/spiderfoot/spiderfoot/__init__.py"
    "/stuff/spiderfoot/spiderfoot/correlation/rule_loader.py"
    "/stuff/spiderfoot/spiderfoot/correlation/schema.py"
    "/stuff/spiderfoot/spiderfoot/correlation/__init__.py"
    "/stuff/spiderfoot/spiderfoot/api/models.py"
    "/stuff/spiderfoot/spiderfoot/api/search_base.py"
    "/stuff/spiderfoot/spiderfoot/api/__init__.py"
    "/stuff/spiderfoot/spiderfoot/cli/__init__.py"
    "/stuff/spiderfoot/spiderfoot/security/__init__.py"
    "/stuff/spiderfoot/spiderfoot/webui/templates.py"
    "/stuff/spiderfoot/spiderfoot/webui/__init__.py"
    "/stuff/spiderfoot/spiderfoot/sflib/core.py"
    "/stuff/spiderfoot/spiderfoot/sflib/__init__.py"
    "/stuff/spiderfoot/spiderfoot/core/__init__.py"
    "/stuff/spiderfoot/spiderfoot/db/__init__.py"
)

{
  echo "## File Timestamps and Sizes"
  echo ""
  echo "| File | Size (bytes) | Modified Date | Access Date |"
  echo "|------|-------------|---------------|-------------|"
} >> "$OUTPUT_FILE"

for file in "${FILES[@]}"; do
    if [ -f "$file" ]; then
        # Use stat to get creation time, modified time, and size
        # Different systems use different stat syntax
        if stat --version &>/dev/null 2>&1; then
            # GNU stat
            size=$(stat -c%s "$file" 2>/dev/null || echo "ERROR")
            mtime=$(stat -c%y "$file" 2>/dev/null | cut -d' ' -f1,2 || echo "ERROR")
            atime=$(stat -c%x "$file" 2>/dev/null | cut -d' ' -f1,2 || echo "ERROR")
        else
            # BSD stat (macOS)
            size=$(stat -f%z "$file" 2>/dev/null || echo "ERROR")
            mtime=$(stat -f%Sm -t "%Y-%m-%d %H:%M:%S" "$file" 2>/dev/null || echo "ERROR")
            atime=$(stat -f%Sa -t "%Y-%m-%d %H:%M:%S" "$file" 2>/dev/null || echo "ERROR")
        fi
        echo "| $file | $size | $mtime | $atime |" >> "$OUTPUT_FILE"
    else
        echo "| $file | FILE NOT FOUND | - | - |" >> "$OUTPUT_FILE"
    fi
done

{
  echo ""
  echo "## Summary Statistics"
  echo ""
} >> "$OUTPUT_FILE"

TOTAL_PYTHON_FILES=$(find /stuff/spiderfoot/spiderfoot -name "*.py" -type f 2>/dev/null | wc -l)
TOTAL_SIZE=$(find /stuff/spiderfoot/spiderfoot -name "*.py" -type f -exec stat -c%s {} + 2>/dev/null | awk '{s+=$1} END {print s}')
RECENT_MODS=$(find /stuff/spiderfoot/spiderfoot -name "*.py" -type f -mmin -120 2>/dev/null | wc -l)

{
  echo "- **Total Python files in spiderfoot/**: $TOTAL_PYTHON_FILES"
  echo "- **Total size of Python files**: $TOTAL_SIZE bytes"
  echo "- **Files modified in last 2 hours**: $RECENT_MODS"
  echo ""
  echo "## Last Modified Check (all Python files)"
  echo ""
  echo "\`\`\`"
  find /stuff/spiderfoot/spiderfoot -name "*.py" -type f -printf "%TY-%Tm-%Td %TH:%TM:%TS %s %p\n" 2>/dev/null | sort -r | head -30
  echo "\`\`\`"
} >> "$OUTPUT_FILE"

echo ""
echo "Audit complete. Report saved to: $OUTPUT_FILE"
cat "$OUTPUT_FILE"
