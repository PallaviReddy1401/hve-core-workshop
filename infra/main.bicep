targetScope = 'subscription'

@description('The Azure Developer CLI environment name.')
@minLength(1)
@maxLength(32)
param environmentName string

@description('The Azure region for all resources.')
param location string

var locationAbbreviations = {
  northcentralus: 'ncus'
}
var locationAbbreviation = locationAbbreviations[location]
var resourceGroupName = 'rg-${environmentName}-${locationAbbreviation}'
var tags = {
  'azd-env-name': environmentName
  application: 'smartassist'
  environment: 'development'
}

resource resourceGroup 'Microsoft.Resources/resourceGroups@2024-11-01' = {
  name: resourceGroupName
  location: location
  tags: tags
}

module resources './modules/resources.bicep' = {
  name: 'smartassist-resources'
  scope: resourceGroup
  params: {
    name: environmentName
    location: location
    tags: tags
  }
}

@description('The deployed resource group name.')
output AZURE_RESOURCE_GROUP string = resourceGroup.name

@description('The Azure Container Registry login server.')
output AZURE_CONTAINER_REGISTRY_ENDPOINT string = resources.outputs.containerRegistryEndpoint

@description('The Azure Container Registry name.')
output AZURE_CONTAINER_REGISTRY_NAME string = resources.outputs.containerRegistryName

@description('The SmartAssist Container App name.')
output AZURE_CONTAINER_APP_NAME string = resources.outputs.containerAppName

@description('The Microsoft Foundry account name.')
output AZURE_AI_ACCOUNT_NAME string = resources.outputs.foundryAccountName

@description('The Microsoft Foundry project name.')
output AZURE_AI_PROJECT_NAME string = resources.outputs.foundryProjectName

@description('The Microsoft Foundry project endpoint.')
output AZURE_AI_PROJECT_ENDPOINT string = resources.outputs.foundryProjectEndpoint

@description('The SmartAssist API endpoint.')
output API_URL string = resources.outputs.apiUrl
