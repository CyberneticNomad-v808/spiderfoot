# SpiderFoot Project Structure & Key Files

This file provides a quick reference for developers and AI assistants working with the SpiderFoot codebase.

## Project Overview
SpiderFoot is an enterprise-grade OSINT automation platform with advanced storage capabilities, AI-powered threat intelligence, and comprehensive security hardening.

## Key Documentation Files

### Core Documentation
- `README.md` - Main project documentation with features and quick start
- `LICENSE` - MIT license
- `requirements.txt` - Python dependencies

### Docker & Deployment
- `Dockerfile` - Multi-stage enterprise Docker build (production-ready)
- `docker-entrypoint.sh` - Container startup script with permissions/database setup
- `docker-compose-examples/` - Directory containing deployment configurations:
  - `docker-compose.yml` - Basic setup
  - `docker-compose-dev.yml` - Development environment
  - `docker-compose-prod.yml` - Full production stack (PostgreSQL, Elasticsearch, Redis, Nginx, monitoring)
  - `deploy-production.sh` - Automated production deployment script
- `documentation/docker_deployment.md` - Docker deployment guide
- `.dockerignore` - Docker build context exclusions

### CI/CD & Automation
- `.github/workflows/` - GitHub Actions automation:
  - `docker-image.yml` - Docker build, test, and publish pipeline
  - `build-artifacts.yml` - Multi-platform package builds (deb, rpm, snap, homebrew)
  - `acceptance_test.yml` - Integration testing
  - `codeql-analysis.yml` - Security analysis
  - `semgrep.yml` - Static analysis
  - `codacy.yml` - Code quality checks

### Application Structure
- `sf.py` - Main SpiderFoot application entry point
- `spiderfoot/` - Core SpiderFoot library
- `modules/` - OSINT modules directory:
  - `sfp__stor_db.py` - Database storage module
  - `sfp__stor_db_advanced.py` - Enterprise storage with connection pooling, load balancing
  - `sfp__stor_elasticsearch.py` - Elasticsearch storage
  - `sfp__ai_threat_intel.py` - AI-powered threat intelligence
  - `sfp__security_hardening.py` - Security enhancements
- `correlations/` - YAML-configurable correlation engine
- `documentation/` - Additional documentation

### Testing
- `test/` - Test suite:
  - `test/integration/test_enterprise_storage_features.py` - Comprehensive enterprise features validation
  - `test/unit/` - Unit tests for modules

### Configuration
- `spiderfoot/dicts/` - Dictionaries and wordlists
- Production configuration templates in `docker-compose-examples/docker-compose-production-files/`

## Build Process

### Quick Build from Source
```bash
# Basic Docker build
docker build -t spiderfoot:local .

# Development with docker-compose
docker-compose -f docker-compose-examples/docker-compose-dev.yml up --build

# Production deployment
cd docker-compose-examples && ./deploy-production.sh
```

### Build Arguments
- `REQUIREMENTS` - Custom requirements file (default: requirements.txt)

### External Tools Integrated
- Nuclei v3.3.9 - Vulnerability scanner
- testssl.sh - SSL/TLS testing
- CMSeeK - CMS detection
- retire.js - JavaScript library vulnerability scanner
- DNSTwist, Whatweb, Nmap - Network tools

## Enterprise Features

### Storage Backends
- SQLite (default)
- PostgreSQL (enterprise, with connection pooling)
- Elasticsearch (advanced search/analytics)

### Monitoring & Analytics
- Prometheus metrics
- Grafana dashboards
- Kibana visualization
- Health checks and alerting

### Security
- Non-root container execution
- SSL/TLS support
- API key authentication
- Input validation and sanitization
- Audit logging

## Key Environment Variables (Production)
- `POSTGRES_HOST`, `POSTGRES_DB`, `POSTGRES_USER`, `POSTGRES_PASSWORD`
- `ELASTICSEARCH_ENABLED`, `ELASTICSEARCH_HOST`, `ELASTICSEARCH_PORT`
- `REDIS_HOST`, `REDIS_PORT`, `REDIS_PASSWORD`
- `SF_API_KEY`, `SF_SECRET_KEY`
- `SF_PRODUCTION=true` for production mode

## Architecture Notes
- Multi-stage Docker build for optimized production images
- Virtual environment isolation for Python dependencies
- Connection pooling and load balancing for database operations
- Bulk operations and buffering for Elasticsearch
- Thread-safe operations with proper locking
- Comprehensive error handling and recovery

## Testing Enterprise Features
Run the enterprise validation suite:
```bash
python test/integration/test_enterprise_storage_features.py
```

## Common File Patterns
- `sfp_*.py` - SpiderFoot modules
- `test_*.py` - Test files
- `docker-compose-*.yml` - Different deployment configurations
- `*.md` - Documentation files

## Development Tips
1. Use docker-compose-dev.yml for development
2. Check .github/workflows/ for CI/CD examples
3. Enterprise features are tested in test/integration/
4. Production deployment is automated via deploy-production.sh
5. All containers run as non-root user 'spiderfoot' (UID 1000)

---
*Generated to assist with SpiderFoot development and AI assistant context*
*Last updated: 2025-09-28*