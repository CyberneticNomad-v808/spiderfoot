#!/usr/bin/env bash
#
# SpiderFoot Test Database Setup
#
# Provisions the test database on the unified-postgres container.
# Idempotent - safe to run multiple times.
#
# Matches conftest.py defaults:
#   DB: spiderfoot_test, User: spiderfoot, Password: test_password
#

set -euo pipefail

# Configuration - matches test/conftest.py defaults
CONTAINER="unified-postgres"
PG_SUPERUSER="postgres"
DB_NAME="spiderfoot_test"
DB_USER="spiderfoot"
# Get password from environment or prompt
if [[ -n "${SPIDERFOOT_DB_PASSWORD:-}" ]]; then
    DB_PASSWORD="${SPIDERFOOT_DB_PASSWORD}"
else
    echo -n "Enter password for '${DB_USER}' user: "
    read -rs DB_PASSWORD
    echo ""
    if [[ -z "${DB_PASSWORD}" ]]; then
        echo "Error: Password cannot be empty"
        exit 1
    fi
fi

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

log_ok()   { echo -e "${GREEN}[OK]${NC} $1"; }
log_info() { echo -e "     $1"; }
log_warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }
log_fail() { echo -e "${RED}[FAIL]${NC} $1"; }

psql_exec() {
    docker exec "${CONTAINER}" psql -U "${PG_SUPERUSER}" -tAc "$1"
}

psql_exec_db() {
    docker exec "${CONTAINER}" psql -U "${PG_SUPERUSER}" -d "$1" -tAc "$2"
}

echo ""
echo "SpiderFoot Test Database Setup"
echo "=============================="
echo ""

# 1. Check docker is available
if ! command -v docker &>/dev/null; then
    log_fail "docker command not found"
    exit 1
fi

# 2. Check container is running
if ! docker ps --format '{{.Names}}' | grep -qx "${CONTAINER}"; then
    log_fail "Container '${CONTAINER}' is not running"
    log_info "Start it with: docker start ${CONTAINER}"
    exit 1
fi
log_ok "Container '${CONTAINER}' is running"

# 3. Create user if it doesn't exist
user_exists=$(psql_exec "SELECT 1 FROM pg_catalog.pg_roles WHERE rolname = '${DB_USER}'" || true)
if [[ "${user_exists}" == "1" ]]; then
    log_ok "User '${DB_USER}' already exists"
else
    psql_exec "CREATE ROLE ${DB_USER} WITH LOGIN PASSWORD '${DB_PASSWORD}'"
    log_ok "Created user '${DB_USER}'"
fi

# 4. Create database if it doesn't exist
db_exists=$(psql_exec "SELECT 1 FROM pg_database WHERE datname = '${DB_NAME}'" || true)
if [[ "${db_exists}" == "1" ]]; then
    log_ok "Database '${DB_NAME}' already exists"
else
    psql_exec "CREATE DATABASE ${DB_NAME} OWNER ${DB_USER}"
    log_ok "Created database '${DB_NAME}'"
fi

# 5. Grant permissions
psql_exec "GRANT ALL PRIVILEGES ON DATABASE ${DB_NAME} TO ${DB_USER}"
psql_exec_db "${DB_NAME}" "GRANT ALL ON SCHEMA public TO ${DB_USER}"
psql_exec_db "${DB_NAME}" "ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO ${DB_USER}"
psql_exec_db "${DB_NAME}" "ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO ${DB_USER}"
log_ok "Permissions granted to '${DB_USER}' on '${DB_NAME}'"

# 6. Verify connectivity as the test user
verify=$(docker exec "${CONTAINER}" psql -U "${DB_USER}" -d "${DB_NAME}" -tAc "SELECT 'connected'" 2>&1 || true)
if [[ "${verify}" == "connected" ]]; then
    log_ok "Verified: ${DB_USER}@${DB_NAME} connection works"
else
    log_warn "Could not verify connection as '${DB_USER}': ${verify}"
    log_info "Check pg_hba.conf allows local/trust auth for '${DB_USER}'"
fi

echo ""
echo "Test database ready. Run tests with:"
echo "  export SPIDERFOOT_DB_TYPE=postgresql"
echo "  export SPIDERFOOT_DB_HOST=unified-postgres.blk.ing"
echo "  export SPIDERFOOT_DB_PORT=5432"
echo "  export SPIDERFOOT_DB_NAME=${DB_NAME}"
echo "  export SPIDERFOOT_DB_USER=${DB_USER}"
echo "  export SPIDERFOOT_DB_PASSWORD='***password_set***'"
echo "  ./test/run unit"
echo ""
echo "Note: Make sure to set SPIDERFOOT_DB_PASSWORD in your environment before running tests."
echo ""
