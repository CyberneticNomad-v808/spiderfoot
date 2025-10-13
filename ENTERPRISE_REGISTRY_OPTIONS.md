# Private Container Registry Options for SpiderFoot Enterprise

## Overview
Your custom SpiderFoot enterprise image (`spiderfoot-enterprise:latest`) needs secure hosting with access control. Here are the best options for your enterprise deployment.

## Registry Options (Ranked by Enterprise Suitability)

### 1. **GitHub Container Registry (ghcr.io) - RECOMMENDED**

**Pros:**
- ✅ **Free private repositories** for personal/organization accounts
- ✅ **Fine-grained access control** with teams and permissions
- ✅ **Integrated with GitHub** - same authentication system
- ✅ **No bandwidth/storage limits** for private repos
- ✅ **Enterprise-grade security** with vulnerability scanning
- ✅ **Easy CI/CD integration** with GitHub Actions
- ✅ **Multi-architecture support**

**Setup:**
```bash
# Login to GitHub Container Registry
echo $GITHUB_TOKEN | docker login ghcr.io -u YOUR_USERNAME --password-stdin

# Tag and push your image
docker tag spiderfoot-enterprise:latest ghcr.io/YOUR_USERNAME/spiderfoot-enterprise:latest
docker push ghcr.io/YOUR_USERNAME/spiderfoot-enterprise:latest
```

**Access Control:**
- Private by default
- Share with specific users/teams
- Token-based authentication
- Organization-level controls

### 2. **AWS Elastic Container Registry (ECR)**

**Pros:**
- ✅ **Enterprise-grade security** with IAM integration
- ✅ **Vulnerability scanning** built-in
- ✅ **Fine-grained permissions** per repository
- ✅ **Private by default**
- ✅ **Lifecycle policies** for image management
- ✅ **Cross-region replication**

**Cons:**
- ❌ **Costs** (storage + data transfer)
- ❌ Requires AWS account and knowledge

**Setup:**
```bash
# Login to ECR
aws ecr get-login-password --region us-west-2 | docker login --username AWS --password-stdin YOUR_ACCOUNT.dkr.ecr.us-west-2.amazonaws.com

# Create repository
aws ecr create-repository --repository-name spiderfoot-enterprise

# Tag and push
docker tag spiderfoot-enterprise:latest YOUR_ACCOUNT.dkr.ecr.us-west-2.amazonaws.com/spiderfoot-enterprise:latest
docker push YOUR_ACCOUNT.dkr.ecr.us-west-2.amazonaws.com/spiderfoot-enterprise:latest
```

### 3. **Self-Hosted Harbor Registry**

**Pros:**
- ✅ **Complete control** over your infrastructure
- ✅ **Enterprise features** (RBAC, replication, scanning)
- ✅ **Open source** and free
- ✅ **Air-gapped deployments** possible
- ✅ **Advanced security** scanning and signing

**Cons:**
- ❌ **Self-managed** infrastructure and maintenance
- ❌ Requires significant setup and expertise

### 4. **Azure Container Registry (ACR)**

**Pros:**
- ✅ **Enterprise security** with Azure AD integration
- ✅ **Geo-replication** for performance
- ✅ **Built-in vulnerability scanning**
- ✅ **Private endpoints** for secure access

**Cons:**
- ❌ **Costs** for storage and bandwidth
- ❌ Requires Azure subscription

### 5. **Google Artifact Registry**

**Pros:**
- ✅ **Regional storage** for compliance
- ✅ **IAM integration** for access control
- ✅ **Vulnerability scanning** with Container Analysis
- ✅ **Private by default**

**Cons:**
- ❌ **Costs** based on storage and egress
- ❌ Requires Google Cloud account

## **RECOMMENDED SOLUTION: GitHub Container Registry**

For your SpiderFoot enterprise deployment, **GitHub Container Registry** is the optimal choice because:

1. **Zero Cost** for private images
2. **Excellent Security** with fine-grained access control
3. **Easy Integration** with existing development workflow
4. **No Infrastructure Management** required
5. **Professional Grade** reliability and performance

## Implementation Guide

### Step 1: Set up GitHub Container Registry

```bash
# Create GitHub Personal Access Token with packages:write permissions
# Go to: GitHub Settings > Developer settings > Personal access tokens > Tokens (classic)
# Select scopes: write:packages, read:packages, delete:packages

# Set environment variables
export GITHUB_TOKEN="your_token_here"
export GITHUB_USERNAME="your_username"

# Login to GitHub Container Registry
echo $GITHUB_TOKEN | docker login ghcr.io -u $GITHUB_USERNAME --password-stdin
```

### Step 2: Tag and Push Your Enterprise Image

```bash
# Tag your custom image for GitHub Container Registry
docker tag spiderfoot-enterprise:latest ghcr.io/$GITHUB_USERNAME/spiderfoot-enterprise:latest
docker tag spiderfoot-enterprise:latest ghcr.io/$GITHUB_USERNAME/spiderfoot-enterprise:v1.0.0

# Push to registry
docker push ghcr.io/$GITHUB_USERNAME/spiderfoot-enterprise:latest
docker push ghcr.io/$GITHUB_USERNAME/spiderfoot-enterprise:v1.0.0
```

### Step 3: Configure Access Control

1. **Make Repository Private**:
   - Go to GitHub package page
   - Settings > Change visibility > Private

2. **Add Team Members**:
   - Settings > Manage Actions access
   - Add users/teams with appropriate permissions

### Step 4: Deploy from Private Registry

```bash
# On your deployment servers
echo $GITHUB_TOKEN | docker login ghcr.io -u $GITHUB_USERNAME --password-stdin

# Pull and run your enterprise image
docker pull ghcr.io/$GITHUB_USERNAME/spiderfoot-enterprise:latest
docker run -d -p 5001:5001 --name spiderfoot-enterprise ghcr.io/$GITHUB_USERNAME/spiderfoot-enterprise:latest
```

### Step 5: Update docker-compose for Enterprise Deployment

```yaml
# docker-compose-enterprise.yml
version: "3.9"
services:
  spiderfoot:
    image: ghcr.io/YOUR_USERNAME/spiderfoot-enterprise:latest
    container_name: spiderfoot-enterprise
    restart: unless-stopped
    ports:
      - "5001:5001"
      - "8001:8001"
    environment:
      - SF_DEVELOPMENT_MODE=false
      - POSTGRES_HOST=postgres
      - POSTGRES_DB=spiderfoot_prod
      - POSTGRES_USER=spiderfoot
      - POSTGRES_PASSWORD=${POSTGRES_PASSWORD}
    volumes:
      - spiderfoot-data:/home/spiderfoot/data
      - spiderfoot-logs:/home/spiderfoot/logs
      - spiderfoot-cache:/home/spiderfoot/cache
```

## Security Best Practices

### Image Security
- ✅ **Regularly update** base images and dependencies
- ✅ **Scan for vulnerabilities** before deployment
- ✅ **Use specific tags** instead of `latest` in production
- ✅ **Sign images** for supply chain security

### Access Control
- ✅ **Use service accounts** for automated deployments
- ✅ **Rotate tokens** regularly
- ✅ **Limit permissions** to minimum required
- ✅ **Audit access** logs regularly

### Network Security
- ✅ **Use private networks** for registry communication
- ✅ **Enable TLS** for all connections
- ✅ **Implement firewall rules** for registry access
- ✅ **Monitor registry access** logs

## Cost Analysis

| Registry | Setup Cost | Monthly Cost | Enterprise Features |
|----------|------------|--------------|-------------------|
| GitHub Container Registry | Free | Free | ✅ Excellent |
| AWS ECR | Free | $0.10/GB + transfer | ✅ Excellent |
| Self-Hosted Harbor | Server costs | Infrastructure | ✅ Excellent |
| Azure ACR | Free | $5/month + storage | ✅ Good |
| Google Artifact Registry | Free | $0.10/GB + egress | ✅ Good |

## Conclusion

**GitHub Container Registry** provides the best combination of:
- **Zero cost** for private enterprise images
- **Enterprise-grade security** and access control
- **Minimal setup** and maintenance overhead
- **Professional reliability** and performance

This makes it the ideal choice for hosting your custom SpiderFoot enterprise image with full access control under your ownership.