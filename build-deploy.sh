#!/bin/bash
# SpiderFoot Build and Deploy Script
#
# Configuration:
# Region: us-central1
# Project: intranet-of-tools
# Repository: blkc-foot-enterprise
# Image: blkc-spiderfoot

set -e  # Exit on error

# Color output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
REGION="us-central1"
PROJECT="intranet-of-tools"
REPOSITORY="blkc-foot-enterprise"
IMAGE_NAME="blkc-spiderfoot"
REGISTRY="${REGION}-docker.pkg.dev/${PROJECT}/${REPOSITORY}/${IMAGE_NAME}"

# Build the image
build_image() {
    echo -e "${GREEN}Building SpiderFoot image...${NC}"

    BUILD_DATE=$(date +'%Y%m%dt%H%M%S')
    BUILD_COMMIT=$(git rev-parse --short HEAD)
    BUILD_VERS=v${BUILD_DATE}---${BUILD_COMMIT}

    #TODO: exit if any are empty

    echo "Build version: ${BUILD_VERS}"

    docker build \
        --build-arg BUILD_DATE=${BUILD_DATE} \
        --build-arg BUILD_COMMIT=${BUILD_COMMIT} \
        -t ${IMAGE_NAME}:${BUILD_VERS} \
        .

    # Tag as latest
    docker tag ${IMAGE_NAME}:${BUILD_VERS} ${IMAGE_NAME}:latest

    echo -e "${GREEN}Build complete: ${IMAGE_NAME}:${BUILD_VERS}${NC}"
    export BUILD_VERS
    set_env_build-vers
}

set_env_build-vers() {
if grep -q "^BUILD_VERS=" /stuff/blking_local_proxy/.env; then
    sed -i "s/^BUILD_VERS=.*/BUILD_VERS=${BUILD_VERS}/" /stuff/blking_local_proxy/.env
else
    echo "BUILD_VERS=${BUILD_VERS}" >> /stuff/blking_local_proxy/.env
fi
}

get_last_build-vers() {

        BUILD_VERS=$(docker images ${IMAGE_NAME} --format "{{.Tag}}" | grep "^v[0-9]" | head -n 1)
	echo $BUILD_VERS

}

# Push to Google Cloud Artifact Registry
push_image() {
    echo -e "${GREEN}Pushing image to Artifact Registry...${NC}"

    if [ -z "$BUILD_VERS" ]; then
 echo -e "${YELLOW}BUILD_VERS not set, detecting most recent image...${NC}"
 get_last_build-vers
 

        if [ -z "$BUILD_VERS" ]; then
            echo -e "${RED}Error: No ${IMAGE_NAME} images found. Run build_image first.${NC}"
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

# Clean local SpiderFoot images
clean_local_images() {
    echo -e "${YELLOW}Cleaning local SpiderFoot images...${NC}"

    # Get list of spiderfoot images
    IMAGES=$(docker images | grep spiderfoot | awk '{print $3}' | sort -u)

    if [ -z "$IMAGES" ]; then
        echo "No SpiderFoot images found locally"
        return 0
    fi

    echo "Found $(echo "$IMAGES" | wc -l) unique image(s)"

    # Try to remove each image
    for img in $IMAGES; do
        $SUDO_CMD docker rmi -f $img 2>/dev/null && echo "Removed $img" || echo "Could not remove $img (may be in use)"
    done

    echo -e "${GREEN}Local cleanup complete${NC}"
}

# Clean images from Google Cloud Artifact Registry
clean_remote_images() {
    echo -e "${YELLOW}Cleaning remote SpiderFoot images from Artifact Registry...${NC}"

    # List all versions
    echo "Fetching image versions..."
    gcloud artifacts docker images list ${REGISTRY} --include-tags --format="value(version)" > /tmp/spiderfoot_versions.txt

    if [ ! -s /tmp/spiderfoot_versions.txt ]; then
        echo "No remote images found"
        return 0
    fi

    echo "Found $(cat /tmp/spiderfoot_versions.txt | wc -l) version(s)"

    # Delete each version
    while read version; do
        echo "Deleting version: ${version}"
        gcloud artifacts docker images delete ${REGISTRY}@${version} --quiet 2>/dev/null || echo "Could not delete ${version}"
    done < /tmp/spiderfoot_versions.txt

    $SUDO_CMD rm -f /tmp/spiderfoot_versions.txt

    echo -e "${GREEN}Remote cleanup complete${NC}"
}

# Stop and remove running SpiderFoot container
stop_container() {
    echo -e "${YELLOW}Stopping SpiderFoot container...${NC}"

    if docker ps -a | grep -q spiderfoot; then
        $SUDO_CMD docker stop spiderfoot 2>/dev/null || true
        $SUDO_CMD docker rm spiderfoot 2>/dev/null || true
        echo -e "${GREEN}Container stopped and removed${NC}"
    else
        echo "No SpiderFoot container found"
    fi
}

# Deploy with docker compose
deploy() {
    if [ -z "$BUILD_VERS" ]; then
 echo -e "${YELLOW}BUILD_VERS not set, detecting most recent image...${NC}"
 get_last_build-vers
 set_env_build-vers
    fi
echo -e "${GREEN}Deploying SpiderFoot...${NC}"

    cd /stuff/blking_local_proxy

    if [ "$VERBOSE" = "true" ]; then
        docker compose up spiderfoot
    else
        docker compose up -d spiderfoot
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
    echo "  clean-local        - Remove all local SpiderFoot images"
    echo "  clean-remote       - Remove all remote SpiderFoot images from Artifact Registry"
    echo "  clean-all          - Remove all local and remote SpiderFoot images"
    echo "  full               - Build, push, stop, and deploy (default)"
    echo ""
    echo "Options:"
    echo "  --verbose, -verbose  - Show container logs during deploy (no -d flag)"
    echo "  --sudo, sudo         - Use sudo for cleaning operations (docker rmi, rm, etc.)"
    echo ""
    echo "Examples:"
    echo "  $0 build"
    echo "  $0 deploy --verbose"
    echo "  $0 clean-local --sudo"
    echo "  $0 clean-all sudo"
}

# Parse flags
VERBOSE="false"
SUDO_CMD=""
for arg in "$@"; do
    if [ "$arg" = "--verbose" ] || [ "$arg" = "-verbose" ]; then
        VERBOSE="true"
    elif [ "$arg" = "--sudo" ] || [ "$arg" = "sudo" ]; then
        SUDO_CMD="sudo"
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
        echo -e "${RED}Unknown command: $1${NC}"
        usage
        exit 1
        ;;
esac
