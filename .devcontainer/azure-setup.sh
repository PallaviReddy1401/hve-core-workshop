#!/bin/bash
set -euo pipefail

echo "=== Azure Resource Provisioning for HVE-Core Workshop ==="
echo ""

# Prompt for configuration values
read -p "Azure region (e.g. eastus2, swedencentral): " LOCATION
read -p "Resource group name: " RG_NAME
read -p "AI Foundry account name (globally unique): " AI_ACCOUNT
read -p "Project name: " PROJECT_NAME
read -p "Model name [gpt-4o]: " MODEL_NAME
MODEL_NAME="${MODEL_NAME:-gpt-4o}"
read -p "Model version [2024-11-20]: " MODEL_VERSION
MODEL_VERSION="${MODEL_VERSION:-2024-11-20}"
read -p "Deployment name [gpt-4o]: " DEPLOYMENT
DEPLOYMENT="${DEPLOYMENT:-gpt-4o}"
: "${LOCATION:?Azure region is required}"
: "${RG_NAME:?Resource group name is required}"
: "${AI_ACCOUNT:?AI Foundry account name is required}"
: "${PROJECT_NAME:?Project name is required}"

echo ""
echo "--- Creating resource group ---"
az group create --name "$RG_NAME" --location "$LOCATION"

echo ""
echo "--- Creating AI Services (Foundry) account ---"
az cognitiveservices account create \
  --name "$AI_ACCOUNT" \
  --resource-group "$RG_NAME" \
  --kind AIServices \
  --sku S0 \
  --location "$LOCATION" \
  --custom-domain "$AI_ACCOUNT" \
  --yes

echo ""
echo "--- Creating Foundry project ---"
az cognitiveservices account project create \
  --resource-group "$RG_NAME" \
  --name "$AI_ACCOUNT" \
  --project-name "$PROJECT_NAME" \
  --location "$LOCATION"

echo ""
echo "--- Deploying $MODEL_NAME model ---"
az cognitiveservices account deployment create \
  --name "$AI_ACCOUNT" \
  --resource-group "$RG_NAME" \
  --deployment-name "$DEPLOYMENT" \
  --model-name "$MODEL_NAME" \
  --model-version "$MODEL_VERSION" \
  --model-format OpenAI \
  --sku-name Standard \
  --sku-capacity 10

echo ""
echo "--- Retrieving endpoint ---"
az cognitiveservices account show \
  --name "$AI_ACCOUNT" \
  --resource-group "$RG_NAME" \
  --query "{endpoint:properties.endpoint}" -o table

echo ""
echo "=== Done! Save the endpoint above for Challenge 7. ==="
