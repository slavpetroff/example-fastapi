#!/bin/bash

# Generate IMAGE_TAG at the start of the script
export IMAGE_TAG=$(date +%Y%m%d%H%M%S)

# Function to read .env and build Helm arguments
build_helm_args() {
  local args=""
  while IFS='=' read -r key value; do
    # Skip empty lines and comments
    [[ $key =~ ^[[:space:]]*$ ]] || [[ $key =~ ^# ]] && continue

    # Remove any leading/trailing whitespace
    key=$(echo $key | xargs)
    value=$(echo $value | xargs)

    # Check if the key is 'image.tag' and remove it
    if [[ $key == "image.tag" ]]; then
      continue
    fi

    # Check if the key is 'image.repo' and remove it
    if [[ $key == "image.repository" ]]; then
      args="${args},${key}=${value}"
    fi

    # Check if the key is entirely lowercase
    if [[ $key =~ ^[a-z0-9._-]+$ ]]; then
      args="${args},${key}=${value}"
      continue
    fi

    # Convert key to lowercase for case-insensitive matching
    lower_key=$(echo "$key" | tr '[:upper:]' '[:lower:]')

    # Check if it's a secret (contains pass, cert, or secret, case-insensitive)
    if [[ $lower_key =~ .*(pass|cert|secret).* || $key == "DATABASE__URL" ]]; then
      args="${args},secret.${key}=${value}"
    else
      args="${args},container_env.${key}=${value}"
    fi
  done < ../.env.dev

  echo "${args:1}" # Remove leading comma
}

# Store current context and namespace
CURRENT_CONTEXT=$(kubectl config current-context)
CURRENT_NAMESPACE=$(kubectl config view --minify -o jsonpath='{..namespace}')

# Set desired context and namespace for deployment
kubectl config use-context microk8s
kubectl config set-context --current --namespace=default

# Get Helm arguments
HELM_ARGS=$(build_helm_args)

# Docker build commands using the generated IMAGE_TAG
docker build --platform linux/amd64,linux/arm64 -t slavpetroff/be:$IMAGE_TAG -f deploy/docker/Dockerfile .
docker push slavpetroff/be:$IMAGE_TAG

# Helm upgrade commands with dynamic environment variables
helm upgrade --install be-worker ./deploy/helm/worker --set image.tag=$IMAGE_TAG,image.repository=slavpetroff/be,${HELM_ARGS}
helm upgrade --install be ./deploy/helm/app --set image.tag=$IMAGE_TAG,image.repository=slavpetroff/be,${HELM_ARGS}
helm upgrade --install prometheus ./deploy/helm/prometheus
helm upgrade --install postgres ./deploy/helm/postgres
helm upgrade --install redis ./deploy/helm/redis
helm upgrade --install grafana ./deploy/helm/grafana
helm upgrade --install tempo ./deploy/helm/tempo
helm upgrade --install loki ./deploy/helm/loki

# Restore original context and namespace
kubectl config use-context $CURRENT_CONTEXT
kubectl config set-context --current --namespace=$CURRENT_NAMESPACE

# Output IMAGE_TAG for reference
echo "Deployment completed with IMAGE_TAG: $IMAGE_TAG"
