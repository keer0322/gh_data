const axios = require('axios');

const vaultAddress = process.argv[2];
const roleId = process.argv[3];
const secretId = process.argv[4];
const vaultSecretPath = process.argv[5];
const circleciToken = process.argv[6];
const circleciOrgSlug = process.argv[7];
const circleciContextId = process.argv[8];

// Function to authenticate to Vault using AppRole and obtain a token
async function getVaultToken() {
  const vaultAuthUrl = `${vaultAddress}/v1/auth/approle/login`;
  
  try {
    const response = await axios.post(vaultAuthUrl, {
      role_id: roleId,
      secret_id: secretId
    });
    return response.data.auth.client_token; // Return the Vault token
  } catch (error) {
    console.error(`Failed to authenticate with Vault using AppRole: ${error.message}`);
    process.exit(1);
  }
}

// Function to fetch secrets from a Vault path using the generated token
async function fetchVaultSecrets(vaultToken) {
  const vaultUrl = `${vaultAddress}/v1/${vaultSecretPath}`;
  const headers = { 'X-Vault-Token': vaultToken };

  try {
    const response = await axios.get(vaultUrl, { headers });
    return response.data.data; // Assuming the secrets are in the 'data' object
  } catch (error) {
    console.error(`Failed to fetch secrets from Vault: ${error.message}`);
    process.exit(1);
  }
}

// Add or update secret in CircleCI Context
async function updateCircleCIContext(secretKey, secretValue) {
  const circleciUrl = `https://circleci.com/api/v2/context/${circleciContextId}/environment-variable`;
  const headers = {
    'Circle-Token': circleciToken,
    'Content-Type': 'application/json',
  };

  try {
    await axios.post(
      circleciUrl,
      { name: secretKey, value: secretValue },
      { headers }
    );
    console.log(`Updated secret '${secretKey}' in CircleCI context`);
  } catch (error) {
    console.error(`Failed to update CircleCI context: ${error.message}`);
    process.exit(1);
  }
}

// Main function to authenticate, fetch secrets, and sync to CircleCI
async function syncVaultToCircleCI() {
  // Step 1: Authenticate and get the Vault token
  const vaultToken = await getVaultToken();

  // Step 2: Fetch the secrets from Vault
  const secrets = await fetchVaultSecrets(vaultToken);

  // Step 3: Loop through each secret from Vault and update CircleCI context
  for (const [key, value] of Object.entries(secrets)) {
    await updateCircleCIContext(key, value);
  }
  
  console.log('Successfully synced all secrets from Vault to CircleCI Context');
}

syncVaultToCircleCI();
