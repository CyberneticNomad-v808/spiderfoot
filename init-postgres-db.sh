#!/bin/bash
# SpiderFoot PostgreSQL Database Initialization Script
# Dynamically detects configuration from .env files and running containers
#
# Usage: ./init-postgres-db.sh [OPTIONS]
#   --image IMAGE_NAME    Docker image to use
#   --container NAME      Container name to use
#   --env-file PATH       Path to .env file

set -e

# =============================================================================
# CONFIGURATION - Set defaults here or pass via command line
# =============================================================================
DEFAULT_CONTAINER_NAME="spiderfoot"
DEFAULT_IMAGE="us-central1-docker.pkg.dev/intranet-of-tools/blkc-foot-enterprise/spiderfoot-enterprise:v1.1.0-postgresql"
DEFAULT_WEB_PORT="5001"
DEFAULT_API_PORT="8001"
DEFAULT_POSTGRES_PORT="5432"

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --image)
            DEFAULT_IMAGE="$2"
            shift 2
            ;;
        --container)
            DEFAULT_CONTAINER_NAME="$2"
            shift 2
            ;;
        --env-file)
            ENV_FILE="$2"
            shift 2
            ;;
        *)
            echo "Unknown option: $1"
            exit 1
            ;;
    esac
done

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

# =============================================================================
# UTILITY FUNCTIONS
# =============================================================================

load_env() {
    local env_file="$1"
    if [ -f "$env_file" ]; then
        echo -e "${BLUE}Loading environment from: $env_file${NC}"
        set -a
        # shellcheck source=/dev/null
        source "$env_file"
        set +a
        return 0
    fi
    return 1
}

prompt_continue() {
    echo -e "\n${YELLOW}Press Enter to continue to the next step, or Ctrl+C to exit...${NC}"
    read -r
}

success() {
    echo -e "${GREEN}✓ $1${NC}"
}

error() {
    echo -e "${RED}✗ $1${NC}"
}

info() {
    echo -e "${YELLOW}$1${NC}"
}

prompt_with_default() {
    local prompt="$1"
    local default="$2"
    local var_name="$3"

    echo -n "$prompt [$default]: "
    read -r input
    eval "$var_name=\"\${input:-$default}\""
}

# =============================================================================
# MAIN SCRIPT
# =============================================================================

echo "========================================"
echo "SpiderFoot PostgreSQL Initialization"
echo "========================================"
echo ""

# Load environment files
info "Looking for configuration files..."
ENV_LOADED=false

if [ -n "$ENV_FILE" ]; then
    if load_env "$ENV_FILE"; then
        ENV_LOADED=true
    fi
else
    for env_path in \
        "/stuff/blking_local_proxy/.env" \
        "/stuff/spiderfoot/.env" \
        "$(pwd)/.env" \
        "../blking_local_proxy/.env"; do
        if load_env "$env_path"; then
            ENV_LOADED=true
            break
        fi
    done
fi

if [ "$ENV_LOADED" = false ]; then
    info "No .env file found - will use defaults and prompts"
fi

echo ""

# =============================================================================
# PostgreSQL Configuration
# =============================================================================
info "Detecting PostgreSQL configuration..."

POSTGRES_HOST=${POSTGRES_HOST:-}
POSTGRES_DB=${POSTGRES_SPIDERFOOT_DB:-${POSTGRES_DB:-}}
POSTGRES_USER=${POSTGRES_SPIDERFOOT_USER:-${POSTGRES_USER:-}}
POSTGRES_PASSWORD=${POSTGRES_SPIDERFOOT_PASSWORD:-${POSTGRES_PASSWORD:-}}
POSTGRES_PORT=${POSTGRES_PORT:-}

# Auto-detect PostgreSQL container if host not set
if [ -z "$POSTGRES_HOST" ]; then
    POSTGRES_CONTAINER=$(docker ps --format '{{.Names}}' | grep -iE 'unified-postgres|postgres' | head -1)
    if [ -n "$POSTGRES_CONTAINER" ]; then
        POSTGRES_HOST="$POSTGRES_CONTAINER"
        success "Auto-detected PostgreSQL container: $POSTGRES_HOST"
    fi
fi

# Prompt for missing values with defaults
prompt_with_default "Enter PostgreSQL host" "${POSTGRES_HOST:-unified-postgres}" POSTGRES_HOST
prompt_with_default "Enter database name" "${POSTGRES_DB:-spiderfoot}" POSTGRES_DB
prompt_with_default "Enter database user" "${POSTGRES_USER:-spiderfoot}" POSTGRES_USER
prompt_with_default "Enter PostgreSQL port" "${POSTGRES_PORT:-$DEFAULT_POSTGRES_PORT}" POSTGRES_PORT

if [ -z "$POSTGRES_PASSWORD" ]; then
    echo -n "Enter database password: "
    read -rs POSTGRES_PASSWORD
    echo ""
    if [ -z "$POSTGRES_PASSWORD" ]; then
        error "Password cannot be empty"
        exit 1
    fi
fi

echo ""
success "PostgreSQL Configuration:"
echo "  Host: $POSTGRES_HOST"
echo "  Database: $POSTGRES_DB"
echo "  User: $POSTGRES_USER"
echo "  Port: $POSTGRES_PORT"

prompt_continue

# =============================================================================
# STEP 1: Drop old workspace table
# =============================================================================
echo ""
echo "STEP 1: Drop old workspace table (if exists)"
echo "--------------------------------------------"
info "This removes tbl_workspaces with incorrect SQLite schema."
echo ""

echo -n "Drop tbl_workspaces table? (y/N): "
read -r DROP_CONFIRM
DROP_CONFIRM=${DROP_CONFIRM:-N}

if [[ $DROP_CONFIRM =~ ^[Yy]$ ]]; then
    if docker exec "$POSTGRES_HOST" psql -U "$POSTGRES_USER" -d "$POSTGRES_DB" \
        -c "DROP TABLE IF EXISTS tbl_workspaces CASCADE;" 2>&1; then
        success "Table dropped successfully"
    else
        error "Failed to drop table (may not exist - this is OK)"
    fi
else
    info "Skipping table drop"
fi

prompt_continue

# =============================================================================
# STEP 2: Start or connect to SpiderFoot container
# =============================================================================
echo ""
echo "STEP 2: SpiderFoot Container Setup"
echo "--------------------------------------------"
echo "Choose an option:"
echo "1) Start NEW SpiderFoot container"
echo "2) Connect to EXISTING running container"
echo ""
echo -n "Enter choice (1 or 2): "
read -r CONTAINER_CHOICE

if [ "$CONTAINER_CHOICE" = "1" ]; then
    info "Starting new SpiderFoot container..."
    echo ""

    # Show and select network
    echo "Available networks:"
    docker network ls --format '{{.Name}}'
    echo ""

    # Detect network from PostgreSQL container
    DETECTED_NETWORK=$(docker inspect "$POSTGRES_HOST" 2>/dev/null | \
        grep -o '"NetworkMode": "[^"]*"' | cut -d'"' -f4 | head -1)

    if [ -n "$DETECTED_NETWORK" ] && [ "$DETECTED_NETWORK" != "default" ]; then
        prompt_with_default "Enter network name" "$DETECTED_NETWORK" NETWORK_NAME
    else
        prompt_with_default "Enter network name" "bridge" NETWORK_NAME
    fi

    # Get image name
    prompt_with_default "Enter image name" "$DEFAULT_IMAGE" IMAGE_NAME

    # Get container name
    prompt_with_default "Enter container name" "$DEFAULT_CONTAINER_NAME" CONTAINER_NAME

    # Get ports
    prompt_with_default "Enter Web UI port" "$DEFAULT_WEB_PORT" WEB_PORT
    prompt_with_default "Enter API port" "$DEFAULT_API_PORT" API_PORT

    # Remove old container if exists
    if docker ps -a --format '{{.Names}}' | grep -q "^${CONTAINER_NAME}$"; then
        info "Removing old container: $CONTAINER_NAME"
        docker rm -f "$CONTAINER_NAME" 2>/dev/null || true
    fi

    # Start container
    info "Starting container..."
    docker run -d --name "$CONTAINER_NAME" \
        --network "$NETWORK_NAME" \
        -e POSTGRES_HOST="$POSTGRES_HOST" \
        -e POSTGRES_DB="$POSTGRES_DB" \
        -e POSTGRES_USER="$POSTGRES_USER" \
        -e POSTGRES_PASSWORD="$POSTGRES_PASSWORD" \
        -e POSTGRES_PORT="$POSTGRES_PORT" \
        -p "${WEB_PORT}:5001" \
        -p "${API_PORT}:8001" \
        "$IMAGE_NAME"

    SPIDERFOOT_CONTAINER="$CONTAINER_NAME"
    SPIDERFOOT_WEB_PORT="$WEB_PORT"
    SPIDERFOOT_API_PORT="$API_PORT"

    info "Waiting 10 seconds for container to start..."
    sleep 10

    success "Container started: $SPIDERFOOT_CONTAINER"

elif [ "$CONTAINER_CHOICE" = "2" ]; then
    info "Looking for existing SpiderFoot containers..."
    echo ""

    # Show running containers
    FOUND_CONTAINERS=$(docker ps --format '{{.Names}}' | grep -i spiderfoot || true)

    if [ -n "$FOUND_CONTAINERS" ]; then
        echo "Found SpiderFoot containers:"
        echo "$FOUND_CONTAINERS"
        echo ""
    fi

    echo -n "Enter container name or ID: "
    read -r SPIDERFOOT_CONTAINER

    if [ -z "$SPIDERFOOT_CONTAINER" ]; then
        error "Container name cannot be empty"
        exit 1
    fi

    if ! docker ps --format '{{.Names}}' | grep -q "^${SPIDERFOOT_CONTAINER}$"; then
        error "Container not found or not running: $SPIDERFOOT_CONTAINER"
        exit 1
    fi

    # Detect ports from container
    PORT_MAPPING=$(docker port "$SPIDERFOOT_CONTAINER" 2>/dev/null || echo "")
    SPIDERFOOT_WEB_PORT=$(echo "$PORT_MAPPING" | grep "5001/tcp" | cut -d':' -f2 | tr -d ' ')
    SPIDERFOOT_API_PORT=$(echo "$PORT_MAPPING" | grep "8001/tcp" | cut -d':' -f2 | tr -d ' ')

    # Use defaults if detection failed
    SPIDERFOOT_WEB_PORT=${SPIDERFOOT_WEB_PORT:-$DEFAULT_WEB_PORT}
    SPIDERFOOT_API_PORT=${SPIDERFOOT_API_PORT:-$DEFAULT_API_PORT}

    success "Connected to existing container: $SPIDERFOOT_CONTAINER"
    info "Detected ports - Web: $SPIDERFOOT_WEB_PORT, API: $SPIDERFOOT_API_PORT"
else
    error "Invalid choice"
    exit 1
fi

# =============================================================================
# URL Configuration
# =============================================================================
echo ""
info "Configuring access URLs..."

# Detect domain and scheme
DOMAIN=${DOMAIN:-localhost}
URL_SCHEME="http"

# Check if SSL is configured in environment
if [ -n "$SSL_CERT_PATH" ] && [ -f "$SSL_CERT_PATH" ]; then
    URL_SCHEME="https"
fi

if [ -n "$DASHBOARD_URL" ]; then
    if [[ "$DASHBOARD_URL" =~ ^https:// ]]; then
        URL_SCHEME="https"
    fi
    DOMAIN=$(echo "$DASHBOARD_URL" | sed -E 's|https?://([^/:]+).*|\1|')
fi

# Build URLs
SPIDERFOOT_WEB_URL="${URL_SCHEME}://${DOMAIN}:${SPIDERFOOT_WEB_PORT}"
SPIDERFOOT_API_URL="${URL_SCHEME}://${DOMAIN}:${SPIDERFOOT_API_PORT}"

echo ""
info "Detected SpiderFoot URLs:"
echo "  Web UI: $SPIDERFOOT_WEB_URL"
echo "  API: $SPIDERFOOT_API_URL"
echo ""
echo -n "Are these URLs correct? (Y/n): "
read -r URL_CONFIRM
URL_CONFIRM=${URL_CONFIRM:-Y}

if [[ ! $URL_CONFIRM =~ ^[Yy]$ ]]; then
    echo -n "Enter Web UI URL: "
    read -r SPIDERFOOT_WEB_URL
    if [ -z "$SPIDERFOOT_WEB_URL" ]; then
        error "Web UI URL cannot be empty"
        exit 1
    fi

    echo -n "Enter API URL: "
    read -r SPIDERFOOT_API_URL
    if [ -z "$SPIDERFOOT_API_URL" ]; then
        error "API URL cannot be empty"
        exit 1
    fi
fi

prompt_continue

# =============================================================================
# STEP 5: Verify database connection
# =============================================================================
echo ""
echo "STEP 5: Verify PostgreSQL Connection"
echo "--------------------------------------------"
info "Checking startup logs..."
echo ""

LOGS=$(docker logs "$SPIDERFOOT_CONTAINER" 2>&1 | tail -50)

if echo "$LOGS" | grep -qi "using postgresql"; then
    success "SpiderFoot is using PostgreSQL"
    echo "$LOGS" | grep -i "using postgresql"
elif echo "$LOGS" | grep -qi "using sqlite"; then
    error "SpiderFoot is using SQLite instead of PostgreSQL!"
    echo "$LOGS" | grep -i "using sqlite"
    echo ""
    echo -n "Database is SQLite. Continue anyway? (y/N): "
    read -r CONTINUE_SQLITE
    CONTINUE_SQLITE=${CONTINUE_SQLITE:-N}
    if [[ ! $CONTINUE_SQLITE =~ ^[Yy]$ ]]; then
        error "Exiting - PostgreSQL not configured"
        exit 1
    fi
else
    info "Could not determine database type from logs"
    echo "Recent logs:"
    echo "$LOGS" | tail -10
fi

prompt_continue

# =============================================================================
# STEP 6: Verify database type programmatically
# =============================================================================
echo ""
echo "STEP 6: Programmatic Database Type Check"
echo "--------------------------------------------"
info "Checking database type via Python..."
echo ""

DB_TYPE=$(docker exec "$SPIDERFOOT_CONTAINER" python3 <<PYEOF
import sys
sys.path.insert(0, '/home/spiderfoot')
try:
    from spiderfoot.db import SpiderFootDb
    config = {
        '__database': 'host=$POSTGRES_HOST dbname=$POSTGRES_DB user=$POSTGRES_USER password=$POSTGRES_PASSWORD port=$POSTGRES_PORT'
    }
    db = SpiderFootDb(config)
    print(f'Database type: {db.db_type}')
except Exception as e:
    print(f'Error: {e}')
    sys.exit(1)
PYEOF
)

if echo "$DB_TYPE" | grep -qi "postgresql"; then
    success "$DB_TYPE"
elif echo "$DB_TYPE" | grep -qi "sqlite"; then
    error "$DB_TYPE"
    echo ""
    echo -n "Detected SQLite. Exit now? (Y/n): "
    read -r EXIT_SQLITE
    EXIT_SQLITE=${EXIT_SQLITE:-Y}
    if [[ $EXIT_SQLITE =~ ^[Yy]$ ]]; then
        error "Exiting - SQLite detected"
        exit 1
    fi
else
    error "Database type check failed:"
    echo "$DB_TYPE"
fi

prompt_continue

# =============================================================================
# STEP 7: Check workspace table schema
# =============================================================================
echo ""
echo "STEP 7: Verify Workspace Table Schema"
echo "--------------------------------------------"
info "Checking if tbl_workspaces has correct PostgreSQL schema..."
echo ""

SCHEMA_CHECK=$(docker exec "$POSTGRES_HOST" psql -U "$POSTGRES_USER" -d "$POSTGRES_DB" \
    -c "\d tbl_workspaces" 2>&1 || echo "TABLE_NOT_FOUND")

if echo "$SCHEMA_CHECK" | grep -q "character varying"; then
    success "Table has PostgreSQL schema (VARCHAR types)"
    echo "$SCHEMA_CHECK"
elif echo "$SCHEMA_CHECK" | grep -qi "did not find\|TABLE_NOT_FOUND"; then
    info "Table does not exist yet - will be created on first use"
else
    error "Table may have incorrect schema:"
    echo "$SCHEMA_CHECK"
fi

prompt_continue

# =============================================================================
# STEP 8: Test workspace creation
# =============================================================================
echo ""
echo "STEP 8: Test Workspace Creation (Optional)"
echo "--------------------------------------------"
echo -n "Test creating a workspace via API? (y/N): "
read -r TEST_WORKSPACE
TEST_WORKSPACE=${TEST_WORKSPACE:-N}

if [[ $TEST_WORKSPACE =~ ^[Yy]$ ]]; then
    info "Creating test workspace via API..."
    info "Using URL: ${SPIDERFOOT_API_URL}/api/workspaces"

    WORKSPACE_RESULT=$(curl -s -X POST "${SPIDERFOOT_API_URL}/api/workspaces" \
        -H "Content-Type: application/json" \
        -d '{"name":"TestWorkspace","description":"Initialization test"}' 2>&1 || echo "CURL_FAILED")

    if echo "$WORKSPACE_RESULT" | grep -qi "workspace_id\|success"; then
        success "Workspace creation test passed"
        echo "$WORKSPACE_RESULT"
    elif echo "$WORKSPACE_RESULT" | grep -qi "CURL_FAILED"; then
        error "API request failed - cannot reach $SPIDERFOOT_API_URL"
    else
        error "Workspace creation test failed:"
        echo "$WORKSPACE_RESULT"
        info "This may be normal if the API endpoint doesn't exist yet"
    fi
else
    info "Skipping workspace test"
fi

# =============================================================================
# Summary
# =============================================================================
echo ""
echo "========================================"
success "Initialization Complete!"
echo "========================================"
echo ""
echo "Summary:"
echo "- PostgreSQL: ${POSTGRES_USER}@${POSTGRES_HOST}:${POSTGRES_PORT}/${POSTGRES_DB}"
echo "- SpiderFoot container: $SPIDERFOOT_CONTAINER"
echo ""
echo "Access SpiderFoot at:"
echo "  Web UI: $SPIDERFOOT_WEB_URL"
echo "  API: $SPIDERFOOT_API_URL"
echo ""
