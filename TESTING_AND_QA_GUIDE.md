# Spiderfoot Testing & Quality Assurance Guide

## Table of Contents
1. [Running Tests](#running-tests)
2. [SonarQube Configuration](#sonarqube-configuration)
3. [Dynamic Analysis for API Contract Issues](#dynamic-analysis)
4. [CI/CD Integration](#cicd-integration)
5. [Best Practices](#best-practices)

---

## Running Tests

### Prerequisites

Install test dependencies:
```bash
pip3 install -r test/requirements.txt
```

### Unit Tests

Run all unit tests:
```bash
# Quick run (from project root)
./test/run

# With coverage
python3 -m pytest test/unit/ --cov=spiderfoot --cov-report=html --cov-report=xml
```

### Integration Tests

Run integration tests (excluding external module tests):
```bash
python3 -m pytest test/integration/ -k "not modules"
```

Run ALL integration tests including module tests (requires API keys):
```bash
python3 -m pytest test/integration/
```

### Full Test Suite

Run everything with parallel execution:
```bash
python3 -m pytest -n auto --flake8 --dist loadfile --durations=5 \
    --cov-report html --cov-report xml --cov=. .
```

### Acceptance Tests (UI/E2E Tests)

Acceptance tests use Robot Framework with Selenium to test the web interface.

**Prerequisites:**
```bash
pip3 install -r test/acceptance/requirements.txt
```

**Run acceptance tests:**
```bash
# Start Spiderfoot web interface
python3 ./sf.py -l 127.0.0.1:5001

# In another terminal, run acceptance tests
cd test/acceptance
robot --variable BROWSER:Firefox --outputdir results scan.robot
```

### Docker-based Testing

Run tests in the same environment as production:
```bash
docker exec -it spiderfoot python3 -m pytest test/unit/ -v
```

---

## SonarQube Configuration

### Setup

A `sonar-project.properties` file has been created with the following features:

**Key Configurations:**
- Python 3.9-3.12 support
- JavaScript/TypeScript analysis for templates
- Coverage report integration
- Security hotspot detection
- Complexity thresholds

### Running SonarQube Scan

**Method 1: Using sonar-scanner (local)**
```bash
# Install sonar-scanner if not already installed
# On Ubuntu/Debian:
# sudo apt-get install sonar-scanner

# Run scan
sonar-scanner \
  -Dsonar.host.url=http://sonarqube.blking.lan \
  -Dsonar.login=YOUR_TOKEN_HERE
```

**Method 2: Using Docker**
```bash
docker run --rm \
    --network blking_private_network \
    -v "$(pwd):/usr/src" \
    sonarsource/sonar-scanner-cli \
    -Dsonar.host.url=http://sonarqube.blking.lan \
    -Dsonar.login=sqp_901b8f8a9aec12adb70a6f70cb8df3ee8be77722
```

**Method 3: Integrated with pytest**
```bash
# Generate coverage report first
python3 -m pytest --cov=spiderfoot --cov-report=xml

# Then run sonar-scanner
sonar-scanner
```

### What SonarQube CAN and CANNOT Detect

**✅ CAN Detect:**
- Code smells and maintainability issues
- Security vulnerabilities (SQL injection, XSS, etc.)
- Bug patterns (null pointer, logic errors)
- Code duplication
- Complexity violations
- Python/JavaScript syntax issues
- Unused variables and imports
- Hardcoded credentials

**❌ CANNOT Detect (without additional configuration):**
- **API contract mismatches** (like the `data.success` bug we fixed)
- Runtime logic errors
- Integration issues between frontend and backend
- Dynamic typing issues in JavaScript
- Missing properties in JSON responses

---

## Dynamic Analysis for API Contract Issues

The bug you encountered (`data.success` being undefined despite API returning targets) requires **runtime** analysis, not just static analysis. Here are solutions:

### 1. API Contract Testing with Pact

**Install Pact:**
```bash
pip install pact-python
```

**Create contract test:**
```python
# test/contract/test_workspace_api_contract.py
from pact import Consumer, Provider
import pytest

@pytest.fixture
def pact():
    pact = Consumer('SpiderfootUI').has_pact_with(
        Provider('SpiderfootAPI'), port=5001
    )
    pact.start_service()
    yield pact
    pact.stop_service()

def test_workspaceget_returns_workspace_object(pact):
    """Contract test: /workspaceget should return workspace object with targets array"""
    expected = {
        'workspace_id': 'ws_test123',
        'name': 'Test Workspace',
        'description': '',
        'created_time': 1234567890.0,
        'modified_time': 1234567890.0,
        'targets': [
            {
                'target_id': 'tgt_test1',
                'value': 'example.com',
                'type': 'INTERNET_NAME'
            }
        ],
        'scans': [],
        'metadata': {}
    }

    (pact
     .given('a workspace with targets exists')
     .upon_receiving('a request for workspace details')
     .with_request('get', '/workspaceget', query={'workspace_id': 'ws_test123'})
     .will_respond_with(200, body=expected))

    with pact:
        # This test will FAIL if the API returns a different structure
        import requests
        response = requests.get('http://localhost:5001/workspaceget?workspace_id=ws_test123')
        data = response.json()

        # These assertions enforce the contract
        assert 'workspace_id' in data
        assert 'targets' in data
        assert 'success' not in data  # Document that success is NOT returned!
```

### 2. JSON Schema Validation

**Create schema definitions:**
```python
# test/schemas/workspace_schemas.py
WORKSPACE_GET_RESPONSE_SCHEMA = {
    "type": "object",
    "required": ["workspace_id", "name", "targets", "scans", "metadata"],
    "properties": {
        "workspace_id": {"type": "string"},
        "name": {"type": "string"},
        "description": {"type": "string"},
        "created_time": {"type": "number"},
        "modified_time": {"type": "number"},
        "targets": {
            "type": "array",
            "items": {
                "type": "object",
                "required": ["target_id", "value", "type"],
                "properties": {
                    "target_id": {"type": "string"},
                    "value": {"type": "string"},
                    "type": {"type": "string"}
                }
            }
        },
        "scans": {"type": "array"},
        "metadata": {"type": "object"}
    },
    "additionalProperties": False  # Fail if unexpected properties like 'success' appear
}
```

**Validation test:**
```python
# test/integration/test_api_contracts.py
import jsonschema
from test.schemas.workspace_schemas import WORKSPACE_GET_RESPONSE_SCHEMA

def test_workspaceget_schema_compliance(client):
    """Ensure /workspaceget returns data matching the documented schema"""
    response = client.get('/workspaceget?workspace_id=test_ws')
    data = response.json()

    # This will raise ValidationError if response doesn't match schema
    jsonschema.validate(instance=data, schema=WORKSPACE_GET_RESPONSE_SCHEMA)
```

### 3. OpenAPI/Swagger Specification

**Create OpenAPI spec:**
```yaml
# spiderfoot/api/openapi.yaml
openapi: 3.0.0
info:
  title: Spiderfoot API
  version: 4.0.0
paths:
  /workspaceget:
    get:
      summary: Get workspace details
      parameters:
        - name: workspace_id
          in: query
          required: true
          schema:
            type: string
      responses:
        '200':
          description: Workspace details
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/Workspace'
components:
  schemas:
    Workspace:
      type: object
      required:
        - workspace_id
        - name
        - targets
        - scans
        - metadata
      properties:
        workspace_id:
          type: string
        name:
          type: string
        description:
          type: string
        created_time:
          type: number
        modified_time:
          type: number
        targets:
          type: array
          items:
            $ref: '#/components/schemas/Target'
        scans:
          type: array
        metadata:
          type: object
    Target:
      type: object
      required:
        - target_id
        - value
        - type
      properties:
        target_id:
          type: string
        value:
          type: string
        type:
          type: string
```

**Validate with pytest-openapi:**
```bash
pip install pytest-swagger
```

```python
# test/integration/test_openapi_compliance.py
from pytest_swagger import swagger

@swagger('/path/to/openapi.yaml')
def test_api_matches_spec():
    """All API endpoints must match OpenAPI specification"""
    pass  # pytest-swagger handles validation automatically
```

### 4. TypeScript for Type Safety

**Convert JavaScript to TypeScript:**

```typescript
// spiderfoot/static/js/workspace.ts
interface Target {
    target_id: string;
    value: string;
    type: string;
    added_time?: number;
    metadata?: any;
}

interface WorkspaceResponse {
    workspace_id: string;
    name: string;
    description: string;
    created_time: number;
    modified_time: number;
    targets: Target[];
    scans: any[];
    metadata: any;
    // NOTE: 'success' is NOT part of the response!
}

function multiTargetScan(workspaceId: string): void {
    $('#scanWorkspaceId').val(workspaceId);

    $.get<WorkspaceResponse>(`${docroot}/workspaceget`, { workspace_id: workspaceId }, function(data) {
        // TypeScript would ERROR here if we tried data.success!
        // Error: Property 'success' does not exist on type 'WorkspaceResponse'

        if (data.targets && data.targets.length > 0) {
            displayTargetSelection(data.targets);
            loadAvailableModules();
            $('#multiTargetScanModal').modal('show');
        } else {
            alertify.confirm(/*...*/);
        }
    }).fail(function() {
        alertify.error('Failed to load workspace targets');
    });
}
```

**Compile TypeScript in your build:**
```bash
npm install --save-dev typescript @types/jquery
npx tsc spiderfoot/static/js/*.ts
```

### 5. Integration Tests for UI Workflows

**Create integration test for the multi-target scan flow:**

```python
# test/integration/test_workspace_ui_workflows.py
import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

@pytest.fixture
def browser():
    driver = webdriver.Firefox()
    driver.get('http://localhost:5001')
    yield driver
    driver.quit()

def test_multi_target_scan_button_opens_modal_when_targets_exist(browser):
    """
    Regression test for bug: Multi-Target Scan should open modal when targets exist

    BUG: Code checked for data.success but API doesn't return success property
    FIX: Remove data.success check from condition
    """
    # Setup: Create workspace with targets
    workspace_id = create_test_workspace_with_targets()

    # Navigate to workspace details
    browser.get(f'http://localhost:5001/workspacedetails?workspace_id={workspace_id}')

    # Click "Multi-Target Scan" button
    multi_target_button = browser.find_element(By.ID, 'multiTargetScanButton')
    multi_target_button.click()

    # ASSERT: Modal should appear (not error dialog)
    modal = WebDriverWait(browser, 5).until(
        EC.visibility_of_element_located((By.ID, 'multiTargetScanModal'))
    )
    assert modal.is_displayed()

    # ASSERT: Target selection should be populated
    target_checkboxes = browser.find_elements(By.CSS_SELECTOR, '#targetSelection input[type="checkbox"]')
    assert len(target_checkboxes) > 0

    # ASSERT: Should NOT show "No Targets Available" alert
    alerts = browser.find_elements(By.CSS_SELECTOR, '.alertify-dialog')
    assert len(alerts) == 0
```

---

## CI/CD Integration

### GitHub Actions Workflow

Create `.github/workflows/quality-assurance.yml`:

```yaml
name: Quality Assurance

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'

      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install -r test/requirements.txt

      - name: Run unit tests
        run: |
          python3 -m pytest test/unit/ --cov=spiderfoot --cov-report=xml --cov-report=html

      - name: Run integration tests
        run: |
          python3 -m pytest test/integration/ -k "not modules" -v

      - name: Upload coverage
        uses: codecov/codecov-action@v3
        with:
          files: ./coverage.xml

  sonarqube:
    runs-on: ubuntu-latest
    needs: test
    steps:
      - uses: actions/checkout@v3
        with:
          fetch-depth: 0  # Shallow clones disabled for better analysis

      - name: SonarQube Scan
        uses: sonarsource/sonarqube-scan-action@master
        env:
          SONAR_TOKEN: ${{ secrets.SONAR_TOKEN }}
          SONAR_HOST_URL: http://sonarqube.blking.lan
```

### Pre-commit Hooks

Install pre-commit:
```bash
pip install pre-commit
```

Create `.pre-commit-config.yaml`:
```yaml
repos:
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.5.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
      - id: check-json
      - id: check-added-large-files

  - repo: https://github.com/psf/black
    rev: 23.12.1
    hooks:
      - id: black
        language_version: python3

  - repo: https://github.com/PyCQA/flake8
    rev: 7.0.0
    hooks:
      - id: flake8
        args: ['--config=setup.cfg']

  - repo: https://github.com/pre-commit/mirrors-eslint
    rev: v8.56.0
    hooks:
      - id: eslint
        files: \.js$
        types: [file]
```

Install hooks:
```bash
pre-commit install
```

---

## Best Practices

### 1. Test-Driven Development (TDD)

For API changes, write the test first:
```python
def test_new_endpoint_returns_expected_structure():
    response = client.get('/newapi')
    data = response.json()

    # Define expected structure
    assert 'field1' in data
    assert 'field2' in data
    assert isinstance(data['field1'], str)
```

### 2. API Documentation

Document API responses in docstrings:
```python
@cherrypy.expose
@cherrypy.tools.json_out()
def workspaceget(self, workspace_id):
    """Get workspace details.

    Args:
        workspace_id: Workspace identifier

    Returns:
        dict: Workspace object with structure:
            {
                "workspace_id": str,
                "name": str,
                "description": str,
                "created_time": float,
                "modified_time": float,
                "targets": List[Target],
                "scans": List[Scan],
                "metadata": dict
            }

        NOTE: Does NOT include 'success' field (reserved for mutation operations)

    Raises:
        Exception: Returns {"error": str} on failure
    """
    # implementation
```

### 3. Continuous Monitoring

Set up monitoring for:
- Test pass/fail rates
- Code coverage trends
- SonarQube quality gate status
- Performance regression

### 4. Regular Audits

Schedule monthly reviews of:
- Failed tests that were disabled
- Skipped SonarQube issues
- Outdated dependencies
- API contract changes

---

## Quick Reference

### Run Tests
```bash
# Unit tests only
python3 -m pytest test/unit/ -v

# With coverage
python3 -m pytest test/unit/ --cov=spiderfoot --cov-report=html

# Full suite
python3 -m pytest -n auto --cov-report xml --cov=.
```

### Run SonarQube
```bash
sonar-scanner -Dsonar.host.url=http://sonarqube.blking.lan -Dsonar.login=YOUR_TOKEN
```

### Validate API Contracts
```bash
# Install dependencies
pip install jsonschema pact-python

# Run contract tests
python3 -m pytest test/contract/ -v
```

---

## Troubleshooting

### Tests Fail in Docker but Pass Locally
- Check environment variables
- Verify database connections
- Check file permissions
- Review network isolation

### SonarQube Scan Fails
- Verify token is valid
- Check network connectivity to SonarQube server
- Ensure coverage.xml exists before scan
- Review sonar-project.properties for syntax errors

### Coverage Reports Missing
- Run tests with `--cov` flag
- Check that `pytest-cov` is installed
- Verify `.coveragerc` configuration

---

**Last Updated:** 2025-10-25
**Maintainer:** BL King Consulting
**Related:** `pytest.ini`, `sonar-project.properties`, `/test/README.md`
