#!/bin/bash
# Run only the 75 implemented integration tests (not the 125 stubs marked as "todo")

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}Running Implemented Integration Tests${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# Check if test list file exists
TEST_LIST_FILE="runnable_integration_tests.txt"
if [ ! -f "$TEST_LIST_FILE" ]; then
    echo -e "${YELLOW}Generating test list...${NC}"
    python3 analyze_tests.py
fi

# Count tests
TOTAL_TESTS=$(wc -l < "$TEST_LIST_FILE")
echo -e "${GREEN}Found $TOTAL_TESTS implemented tests to run${NC}"
echo ""

# Parse arguments
WORKERS="${1:-8}"
TIMEOUT="${2:-30}"
VERBOSE=""
STOP_ON_FAIL=""

while [[ $# -gt 0 ]]; do
    case $1 in
        -v|--verbose)
            VERBOSE="-v"
            shift
            ;;
        -x|--stop-on-fail)
            STOP_ON_FAIL="-x"
            shift
            ;;
        -n|--workers)
            WORKERS="$2"
            shift 2
            ;;
        -t|--timeout)
            TIMEOUT="$2"
            shift 2
            ;;
        *)
            shift
            ;;
    esac
done

echo -e "${BLUE}Configuration:${NC}"
echo -e "  Workers: ${WORKERS}"
echo -e "  Timeout: ${TIMEOUT}s per test"
echo -e "  Verbose: ${VERBOSE:-no}"
echo -e "  Stop on fail: ${STOP_ON_FAIL:-no}"
echo ""

# Read tests from file
mapfile -t TESTS < "$TEST_LIST_FILE"

# Run tests
echo -e "${GREEN}Starting test run...${NC}"
echo ""

op run --env-file='./test/.env.test' -- pytest \
    -n "$WORKERS" \
    --timeout="$TIMEOUT" \
    --tb=short \
    $VERBOSE \
    $STOP_ON_FAIL \
    "${TESTS[@]}"

EXIT_CODE=$?

echo ""
if [ $EXIT_CODE -eq 0 ]; then
    echo -e "${GREEN}✅ All implemented integration tests passed!${NC}"
else
    echo -e "${RED}❌ Some tests failed (exit code: $EXIT_CODE)${NC}"
fi

exit $EXIT_CODE
