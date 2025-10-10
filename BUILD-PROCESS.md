  # 1. Build the image with build arguments
  docker build \
    --build-arg BUILD_DATE=$(date -u +'%Y-%m-%dT%H:%M:%SZ') \
    --build-arg BUILD_COMMIT=$(git rev-parse --short HEAD) \
    -t spiderfoot:latest \
    .

  # 2. Tag for GCloud Artifact Registry
  # Replace with your actual values:
  #   REGION: e.g., us-central1, us-east1, etc.
  #   PROJECT_ID: your GCP project ID
  #   REPOSITORY: your artifact registry repository name
  docker tag spiderfoot:latest \
    REGION-docker.pkg.dev/PROJECT_ID/REPOSITORY/spiderfoot:latest

  # Optional: Also tag with version/commit
  docker tag spiderfoot:latest \
    REGION-docker.pkg.dev/PROJECT_ID/REPOSITORY/spiderfoot:$(git rev-parse --short HEAD)

  # 3. Configure Docker authentication for GCloud (if not already done)
  gcloud auth configure-docker REGION-docker.pkg.dev

  # 4. Push to Artifact Registry
  docker push REGION-docker.pkg.dev/PROJECT_ID/REPOSITORY/spiderfoot:latest
  docker push REGION-docker.pkg.dev/PROJECT_ID/REPOSITORY/spiderfoot:$(git rev-parse --short HEAD)

  Example with actual values:
  # If your setup is:
  # Region: us-central1
  # Project: my-project-123
  # Repository: spiderfoot-repo

  docker build \
    --build-arg BUILD_DATE=$(date -u +'%Y-%m-%dT%H:%M:%SZ') \
    --build-arg BUILD_COMMIT=$(git rev-parse --short HEAD) \
    -t spiderfoot:latest \
    .

  docker tag spiderfoot:latest \
    us-central1-docker.pkg.dev/my-project-123/spiderfoot-repo/spiderfoot:latest

  gcloud auth configure-docker us-central1-docker.pkg.dev

  docker push us-central1-docker.pkg.dev/my-project-123/spiderfoot-repo/spiderfoot:latest

  The build includes metadata injection via BUILD_DATE and BUILD_COMMIT arguments, which gets written to
  /home/spiderfoot/BUILD_INFO in the image.
