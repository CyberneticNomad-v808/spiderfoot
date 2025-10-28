#!/usr/bin/env python3
"""
Fix Spiderfoot correlation YAML schema errors.

The current schema has:
collections:
  collect:
    - method: exact
      field: type
      value: FOO

But should be:
collections:
  - id: "collection_1"
    name: "Collected Items"
    condition:
      collect:
        - method: exact
          field: type
          value: FOO
"""

import yaml
import os
import sys
from pathlib import Path

def fix_correlation_file(filepath):
    """Fix a single correlation YAML file."""
    with open(filepath, 'r') as f:
        data = yaml.safe_load(f)

    # Check if collections needs fixing
    if 'collections' in data and isinstance(data['collections'], dict):
        if 'collect' in data['collections']:
            # Old format detected - fix it
            collect_data = data['collections']['collect']

            # Create new collections array format
            data['collections'] = [
                {
                    'id': f"{data['id']}_collection",
                    'name': data['meta']['name'],
                    'condition': {
                        'collect': collect_data
                    }
                }
            ]

            # Write fixed file
            with open(filepath, 'w') as f:
                yaml.dump(data, f, default_flow_style=False, sort_keys=False)

            return True

    return False

def main():
    correlations_dir = Path('/stuff/spiderfoot/correlations')

    if not correlations_dir.exists():
        print(f"ERROR: {correlations_dir} does not exist")
        sys.exit(1)

    yaml_files = list(correlations_dir.glob('*.yaml'))
    print(f"Found {len(yaml_files)} YAML files in {correlations_dir}")

    fixed_count = 0
    for yaml_file in yaml_files:
        try:
            if fix_correlation_file(yaml_file):
                print(f"✓ Fixed: {yaml_file.name}")
                fixed_count += 1
            else:
                print(f"  Skipped (already correct): {yaml_file.name}")
        except Exception as e:
            print(f"✗ ERROR fixing {yaml_file.name}: {e}")

    print(f"\nFixed {fixed_count}/{len(yaml_files)} files")

if __name__ == '__main__':
    main()
