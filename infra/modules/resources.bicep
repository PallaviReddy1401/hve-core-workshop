targetScope = 'resourceGroup'

@description('The base name for the deployment.')
param name string

@description('The Azure region for all resources.')
param location string

@description('Tags applied to all resources.')
param tags object

var resourceToken = take(uniqueString(subscription().id, resourceGroup().id, name, location), 6)
var alphanumericName = toLower(replace(name, '-', ''))
var containerRegistryName = take('cr${alphanumericName}${resourceToken}', 50)
var identityName = 'id-${name}-api'
var logAnalyticsName = 'log-${name}'
var applicationInsightsName = 'appi-${name}'
var containerAppsEnvironmentName = 'cae-${name}'
var containerAppName = 'ca-${name}-api'
var foundryAccountName = take('ai-${name}-${resourceToken}', 64)
var foundryProjectName = 'smartassist'
var modelDeploymentName = 'smartassist-gpt-41-mini'
var containerAppTags = union(tags, {
  'azd-service-name': 'api'
})
var foundryProjectEndpointValue = 'https://${foundryAccountName}.services.ai.azure.com/api/projects/${foundryProjectName}'
var foundryUserRoleDefinitionId = subscriptionResourceId(
  'Microsoft.Authorization/roleDefinitions',
  '53ca6127-db72-4b80-b1b0-d745d6d5456d'
)

module identity 'br/public:avm/res/managed-identity/user-assigned-identity:0.6.0' = {
  name: 'managed-identity'
  params: {
    name: identityName
    location: location
    tags: tags
    enableTelemetry: false
  }
}

module logAnalytics 'br/public:avm/res/operational-insights/workspace:0.16.0' = {
  name: 'log-analytics'
  params: {
    name: logAnalyticsName
    location: location
    skuName: 'PerGB2018'
    dataRetention: 30
    forceCmkForQuery: false
    tags: tags
    enableTelemetry: false
  }
}

module applicationInsights 'br/public:avm/res/insights/component:0.8.0' = {
  name: 'application-insights'
  params: {
    name: applicationInsightsName
    location: location
    workspaceResourceId: logAnalytics.outputs.resourceId
    applicationType: 'web'
    disableIpMasking: false
    disableLocalAuth: false
    retentionInDays: 30
    samplingPercentage: 100
    tags: tags
    enableTelemetry: false
  }
}

module containerRegistry 'br/public:avm/res/container-registry/registry:0.13.0' = {
  name: 'container-registry'
  params: {
    name: containerRegistryName
    location: location
    acrSku: 'Basic'
    acrAdminUserEnabled: false
    publicNetworkAccess: 'Enabled'
    networkRuleSetDefaultAction: 'Allow'
    roleAssignments: [
      {
        principalId: identity.outputs.principalId
        principalType: 'ServicePrincipal'
        roleDefinitionIdOrName: 'AcrPull'
      }
    ]
    tags: tags
    enableTelemetry: false
  }
}

module foundryAccount 'br/public:avm/res/cognitive-services/account:0.19.0' = {
  name: 'foundry-account'
  params: {
    name: foundryAccountName
    kind: 'AIServices'
    sku: 'S0'
    location: location
    customSubDomainName: foundryAccountName
    allowProjectManagement: true
    managedIdentities: {
      systemAssigned: true
    }
    disableLocalAuth: true
    publicNetworkAccess: 'Enabled'
    deployments: [
      {
        name: modelDeploymentName
        model: {
          format: 'OpenAI'
          name: 'gpt-4.1-mini'
          version: '2025-04-14'
        }
        sku: {
          name: 'GlobalStandard'
          capacity: 10
        }
        versionUpgradeOption: 'NoAutoUpgrade'
      }
    ]
    roleAssignments: [
      {
        principalId: identity.outputs.principalId
        principalType: 'ServicePrincipal'
        roleDefinitionIdOrName: 'Cognitive Services OpenAI User'
      }
    ]
    tags: tags
    enableTelemetry: false
  }
}

resource foundryAccountResource 'Microsoft.CognitiveServices/accounts@2025-06-01' existing = {
  name: foundryAccountName
}

resource foundryProject 'Microsoft.CognitiveServices/accounts/projects@2025-06-01' = {
  parent: foundryAccountResource
  name: foundryProjectName
  location: location
  identity: {
    type: 'UserAssigned'
    userAssignedIdentities: {
      '${resourceId('Microsoft.ManagedIdentity/userAssignedIdentities', identityName)}': {}
    }
  }
  properties: {
    displayName: 'SmartAssist'
    description: 'Microsoft Foundry project for the SmartAssist workshop deployment.'
  }
  tags: tags
  dependsOn: [
    foundryAccount
    identity
  ]
}

resource foundryProjectUserRole 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  name: guid(foundryProject.id, identityName, foundryUserRoleDefinitionId)
  scope: foundryProject
  properties: {
    roleDefinitionId: foundryUserRoleDefinitionId
    principalId: identity.outputs.principalId
    principalType: 'ServicePrincipal'
  }
}

module containerAppsEnvironment 'br/public:avm/res/app/managed-environment:0.16.0' = {
  name: 'container-apps-environment'
  params: {
    name: containerAppsEnvironmentName
    location: location
    publicNetworkAccess: 'Enabled'
    zoneRedundant: false
    peerTrafficEncryption: true
    appLogsConfiguration: {
      destination: 'log-analytics'
      logAnalyticsWorkspaceResourceId: logAnalytics.outputs.resourceId
    }
    tags: tags
    enableTelemetry: false
  }
}

module containerApp 'br/public:avm/res/app/container-app:0.23.0' = {
  name: 'container-app'
  params: {
    name: containerAppName
    location: location
    environmentResourceId: containerAppsEnvironment.outputs.resourceId
    activeRevisionsMode: 'Single'
    ingressExternal: true
    ingressAllowInsecure: false
    ingressTargetPort: 8000
    ingressTransport: 'auto'
    scaleSettings: {
      minReplicas: 0
      maxReplicas: 1
    }
    managedIdentities: {
      userAssignedResourceIds: [
        identity.outputs.resourceId
      ]
    }
    registries: [
      {
        server: containerRegistry.outputs.loginServer
        identity: identity.outputs.resourceId
      }
    ]
    secrets: [
      {
        name: 'applicationinsights-connection-string'
        value: applicationInsights.outputs.connectionString
      }
    ]
    containers: [
      {
        name: 'api'
        image: 'mcr.microsoft.com/azuredocs/containerapps-helloworld:latest'
        env: [
          {
            name: 'SMARTASSIST_MODEL_PROVIDER'
            value: 'foundry'
          }
          {
            name: 'SMARTASSIST_FOUNDRY_PROJECT_ENDPOINT'
            value: foundryProjectEndpointValue
          }
          {
            name: 'SMARTASSIST_FOUNDRY_MODEL_DEPLOYMENT_NAME'
            value: modelDeploymentName
          }
          {
            name: 'AZURE_CLIENT_ID'
            value: identity.outputs.clientId
          }
          {
            name: 'APPLICATIONINSIGHTS_CONNECTION_STRING'
            secretRef: 'applicationinsights-connection-string'
          }
          {
            name: 'OTEL_SERVICE_NAME'
            value: 'smartassist-api'
          }
        ]
        probes: [
          {
            type: 'Startup'
            httpGet: {
              path: '/health'
              port: 8000
            }
            initialDelaySeconds: 1
            periodSeconds: 30
            failureThreshold: 10
            timeoutSeconds: 5
          }
          {
            type: 'Liveness'
            httpGet: {
              path: '/health'
              port: 8000
            }
            initialDelaySeconds: 10
            periodSeconds: 30
            failureThreshold: 3
            timeoutSeconds: 5
          }
          {
            type: 'Readiness'
            httpGet: {
              path: '/health/ready'
              port: 8000
            }
            initialDelaySeconds: 5
            periodSeconds: 10
            failureThreshold: 3
            timeoutSeconds: 5
          }
        ]
        resources: {
          cpu: json('0.5')
          memory: '1Gi'
        }
      }
    ]
    diagnosticSettings: [
      {
        workspaceResourceId: logAnalytics.outputs.resourceId
      }
    ]
    tags: containerAppTags
    enableTelemetry: false
  }
  dependsOn: [
    foundryProjectUserRole
  ]
}

@description('The Azure Container Registry login server.')
output containerRegistryEndpoint string = containerRegistry.outputs.loginServer

@description('The Azure Container Registry name.')
output containerRegistryName string = containerRegistry.outputs.name

@description('The SmartAssist Container App name.')
output containerAppName string = containerApp.outputs.name

@description('The Microsoft Foundry account name.')
output foundryAccountName string = foundryAccount.outputs.name

@description('The Microsoft Foundry project name.')
output foundryProjectName string = foundryProject.name

@description('The Microsoft Foundry project endpoint.')
output foundryProjectEndpoint string = foundryProjectEndpointValue

@description('The SmartAssist API URL.')
output apiUrl string = 'https://${containerApp.outputs.fqdn}'
