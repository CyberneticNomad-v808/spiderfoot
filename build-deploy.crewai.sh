#!/bin/bash
# CrewAI-Studio Build and Deploy Script
#
# Configuration:
# Region: us-central1
# Project: intranet-of-tools
# Repository: crewai-studio-enterprise
# Image: crewai-studio

set -e  # Exit on error

# Color output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
REGION="us-central1"
PROJECT="intranet-of-tools"
REPOSITORY="crewai-studio-enterprise"
IMAGE_NAME="crewai-studio"
REGISTRY="${REGION}-docker.pkg.dev/${PROJECT}/${REPOSITORY}/${IMAGE_NAME}"
DEPLOY_DIR="/stuff/CrewAI-Studio"
DOCKER_FILE="${DEPLOY_DIR}/Dockerfile"
# Build the image
build_image() {
    echo -e "${GREEN}Building CrewAI-Studio image...${NC}"

    BUILD_DATE=$(date +'%Y%m%dt%H%M%S')
    BUILD_COMMIT=$(git rev-parse --short HEAD 2>/dev/null || echo "unknown")
    BUILD_VERS=v${BUILD_DATE}---${BUILD_COMMIT}

    # Validate required variables
    if [ -z "$BUILD_DATE" ] || [ -z "$BUILD_COMMIT" ]; then
        echo -e "${RED}Error: Failed to generate build version${NC}"
        exit 1
    fi

    echo "Build version: ${BUILD_VERS}"

    docker build \
        -f "${DOCKER_FILE}" \
        --build-arg BUILD_DATE="${BUILD_DATE}" \
        --build-arg BUILD_COMMIT="${BUILD_COMMIT}" \
        -t "${IMAGE_NAME}:${BUILD_VERS}" \
        "${DEPLOY_DIR}"

    # Tag as latest
    docker tag ${IMAGE_NAME}:${BUILD_VERS} ${IMAGE_NAME}:latest

    echo -e "${GREEN}Build complete: ${IMAGE_NAME}:${BUILD_VERS}${NC}"
    export BUILD_VERS
    set_env_build_vers
}

# Set BUILD_VERS in .env file
set_env_build_vers() {
    local env_file="${DEPLOY_DIR}/.env"

    if [ ! -f "$env_file" ]; then
        echo -e "${YELLOW}Warning: .env file not found at ${env_file}${NC}"
        echo "BUILD_VERS=${BUILD_VERS}" > "$env_file"
        echo -e "${GREEN}Created .env file with BUILD_VERS${NC}"
        return 0
    fi

    if grep -q "^BUILD_VERS=" "$env_file"; then
        sed -i "s/^BUILD_VERS=.*/BUILD_VERS=${BUILD_VERS}/" "$env_file"
        echo -e "${GREEN}Updated BUILD_VERS in .env${NC}"
    else
        echo "BUILD_VERS=${BUILD_VERS}" >> "$env_file"
        echo -e "${GREEN}Added BUILD_VERS to .env${NC}"
    fi
}

# Get the most recent build version from local images
get_last_build_vers() {
    local last_vers=$(docker images ${IMAGE_NAME} --format "{{.Tag}}" | grep "^v[0-9]" | head -n 1)

    if [ -z "$last_vers" ]; then
        echo -e "${RED}Error: No ${IMAGE_NAME} images found. Run build_image first.${NC}"
        return 1
    fi

    echo "$last_vers"
}

# Push to Google Cloud Artifact Registry
push_image() {
    echo -e "${GREEN}Pushing image to Artifact Registry...${NC}"

    if [ -z "$BUILD_VERS" ]; then
        echo -e "${YELLOW}BUILD_VERS not set, detecting most recent image...${NC}"
        BUILD_VERS=$(get_last_build_vers)

        if [ $? -ne 0 ] || [ -z "$BUILD_VERS" ]; then
            echo -e "${RED}Error: Could not determine BUILD_VERS${NC}"
            return 1
        fi

        echo -e "${GREEN}Using detected version: ${BUILD_VERS}${NC}"
    fi

    # Authenticate with gcloud
    gcloud auth configure-docker ${REGION}-docker.pkg.dev --quiet

    # Tag for registry
    docker tag ${IMAGE_NAME}:${BUILD_VERS} ${REGISTRY}:${BUILD_VERS}
    docker tag ${IMAGE_NAME}:latest ${REGISTRY}:latest

    # Push both tags
    docker push ${REGISTRY}:${BUILD_VERS}
    docker push ${REGISTRY}:latest

    echo -e "${GREEN}Push complete${NC}"
}

# Clean local CrewAI-Studio images
clean_local_images() {
    echo -e "${YELLOW}Cleaning local CrewAI-Studio images...${NC}"

    # Calculate grace period (5 minutes ago in epoch seconds)
    local grace_period=$(date -d '5 minutes ago' +%s)
    local removed=0
    local skipped=0
    local failed=0

    # Get list of crewai-studio images
    IMAGES=$(docker images | grep "${IMAGE_NAME}" | awk '{print $3}' | sort -u)

    if [ -z "$IMAGES" ]; then
        echo "No CrewAI-Studio images found locally"
        return 0
    fi

    echo "Found $(echo "$IMAGES" | wc -l) unique image(s)"
    echo "Grace period: Not deleting images created within last 5 minutes"

    # Try to remove each image
    for img in $IMAGES; do
        # Get image creation time
        local created=$(docker inspect --format='{{.Created}}' $img 2>/dev/null)

        if [ -z "$created" ]; then
            echo "Could not inspect image $img, skipping"
            ((failed++))
            continue
        fi

        # Convert to epoch seconds
        local created_epoch=$(date -d "$created" +%s 2>/dev/null)

        # Check if image is within grace period
        if [ $created_epoch -gt $grace_period ]; then
            echo "Skipping $img (created within last 5 minutes)"
            ((skipped++))
        else
            if docker rmi -f $img 2>/dev/null; then
                echo "Removed $img"
                ((removed++))
            else
                echo "Could not remove $img (may be in use)"
                ((failed++))
            fi
        fi
    done

    echo ""
    echo "Summary: Removed: $removed, Skipped: $skipped, Failed: $failed"
    echo -e "${GREEN}Local cleanup complete${NC}"
}

# Clean images from Google Cloud Artifact Registry
clean_remote_images() {
    echo -e "${YELLOW}Cleaning remote CrewAI-Studio images from Artifact Registry...${NC}"

    # Calculate grace period (5 minutes ago in epoch seconds)
    local grace_period=$(date -d '5 minutes ago' +%s)
    local removed=0
    local skipped=0
    local failed=0

    # List all versions with creation time
    echo "Fetching image versions with timestamps..."
    gcloud artifacts docker images list ${REGISTRY} --include-tags \
        --format="csv[no-heading](version,CREATE_TIME)" > /tmp/crewai_studio_versions.txt

    if [ ! -s /tmp/crewai_studio_versions.txt ]; then
        echo "No remote images found"
        return 0
    fi

    echo "Found $(cat /tmp/crewai_studio_versions.txt | wc -l) version(s)"
    echo "Grace period: Not deleting images created within last 5 minutes"

    # Delete each version, checking grace period
    while IFS=',' read -r version create_time; do
        # Convert creation time to epoch seconds
        local created_epoch=$(date -d "$create_time" +%s 2>/dev/null)

        if [ -z "$created_epoch" ]; then
            echo "Could not parse creation time for ${version}, skipping"
            ((failed++))
            continue
        fi

        # Check if image is within grace period
        if [ $created_epoch -gt $grace_period ]; then
            echo "Skipping ${version} (created within last 5 minutes)"
            ((skipped++))
        else
            echo "Deleting version: ${version}"
            if gcloud artifacts docker images delete ${REGISTRY}@${version} --quiet 2>/dev/null; then
                ((removed++))
            else
                echo "Could not delete ${version}"
                ((failed++))
            fi
        fi
    done < /tmp/crewai_studio_versions.txt

    rm -f /tmp/crewai_studio_versions.txt

    echo ""
    echo "Summary: Removed: $removed, Skipped: $skipped, Failed: $failed"
    echo -e "${GREEN}Remote cleanup complete${NC}"
}

# Stop and remove running CrewAI-Studio container
stop_container() {
    echo -e "${YELLOW}Stopping CrewAI-Studio container...${NC}"

    if docker ps -a | grep -q "${IMAGE_NAME}"; then
        docker stop ${IMAGE_NAME} 2>/dev/null || true
        docker rm ${IMAGE_NAME} 2>/dev/null || true
        echo -e "${GREEN}Container stopped and removed${NC}"
    else
        echo "No CrewAI-Studio container found"
    fi
}

# Deploy with docker compose
deploy() {
    if [ -z "$BUILD_VERS" ]; then
        echo -e "${YELLOW}BUILD_VERS not set, detecting most recent image...${NC}"
        BUILD_VERS=$(get_last_build_vers)

        if [ $? -ne 0 ] || [ -z "$BUILD_VERS" ]; then
            echo -e "${RED}Error: Could not determine BUILD_VERS${NC}"
            return 1
        fi

        set_env_build_vers
    fi

    echo -e "${GREEN}Deploying CrewAI-Studio...${NC}"

    cd ${DEPLOY_DIR}

    if [ ! -f "docker-compose.yml" ]; then
        echo -e "${RED}Error: docker-compose.yml not found in ${DEPLOY_DIR}${NC}"
        return 1
    fi

    if [ "$VERBOSE" = "true" ]; then
        docker compose up ${IMAGE_NAME}
    else
        docker compose up -d ${IMAGE_NAME}
    fi

    echo -e "${GREEN}Deployment complete${NC}"
}

# Full build and deploy workflow
full_deploy() {
    echo -e "${GREEN}=== Full Build and Deploy ===${NC}"
    build_image
    push_image
    stop_container
    deploy
    echo -e "${GREEN}=== Deploy Complete ===${NC}"
}

# Show usage
usage() {
    echo "Usage: $0 [command] [options]"
    echo ""
    echo "Commands:"
    echo "  build              - Build the Docker image"
    echo "  push               - Push image to Artifact Registry"
    echo "  deploy             - Deploy with docker compose"
    echo "  stop               - Stop and remove running container"
    echo "  clean-local        - Remove local CrewAI-Studio images (protects images < 5 min old)"
    echo "  clean-remote       - Remove remote CrewAI-Studio images (protects images < 5 min old)"
    echo "  clean-all          - Remove all local and remote images (protects images < 5 min old)"
    echo "  full               - Build, push, stop, and deploy"
    echo ""
    echo "Options:"
    echo "  --verbose, -verbose  - Show container logs during deploy (no -d flag)"
    echo ""
    echo "Examples:"
    echo "  $0 build"
    echo "  $0 deploy --verbose"
    echo "  $0 full"
}

# Parse flags
VERBOSE="false"
for arg in "$@"; do
    if [ "$arg" = "--verbose" ] || [ "$arg" = "-verbose" ]; then
        VERBOSE="true"
    fi
done

# Main script logic
case "${1}" in
    build)
        build_image
        ;;
    push)
        push_image
        ;;
    deploy)
        deploy
        ;;
    stop)
        stop_container
        ;;
    clean-local)
        stop_container
        clean_local_images
        ;;
    clean-remote)
        clean_remote_images
        ;;
    clean-all)
        stop_container
        clean_local_images
        clean_remote_images
        ;;
    full)
        full_deploy
        ;;
    help|--help|-h)
        usage
        ;;
    *)
        if [ -z "$1" ]; then
            usage
        else
            echo -e "${RED}Unknown command: $1${NC}"
            usage
            exit 1
        fi
        ;;
esac
