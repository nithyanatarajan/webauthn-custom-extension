// register.js
import { base64urlToBuffer, prepareRegistrationAttestationPayload } from './utils.js';
import { invokeExtensionFunctions } from './extensions.js';
import { beginRegistration, completeRegistration } from './api/register.js';

export async function registerPasskey(username) {
  // 1. Begin registration with RP backend
  const { publicKey, challenge_token } = await beginRegistration(username);

  // 2. Convert challenge and user.id
  publicKey.challenge = base64urlToBuffer(publicKey.challenge);
  publicKey.user.id = base64urlToBuffer(publicKey.user.id);

  if (publicKey.excludeCredentials) {
    publicKey.excludeCredentials = publicKey.excludeCredentials.map((cred) => ({
      ...cred,
      id: base64urlToBuffer(cred.id),
    }));
  }

  // 3. Process extensions
  const extensionsAfterProcessing = invokeExtensionFunctions(publicKey.extensions);

  // 4. Call WebAuthn API
  const credential = await navigator.credentials.create({
    publicKey: publicKey,
  });

  if (!credential) {
    throw new Error('Credential creation failed or was cancelled.');
  }

  // 5. Prepare attestation object
  const attestation = prepareRegistrationAttestationPayload(credential, extensionsAfterProcessing);

  // 6. Call RP backend to complete registration
  return await completeRegistration({ attestation, challenge_token });
}
