import { base64urlToBuffer, prepareAuthenticationAssertionPayload } from './utils.js';
import { beginAuthentication, completeAuthentication } from './api/auth.js';
import { invokeExtensionFunctions } from './extensions.js';

export async function authenticateWithPasskey(username) {
  // 1. Begin authentication with RP backend
  const { publicKey, challenge_token } = await beginAuthentication(username);

  // 2. Convert to ArrayBuffers
  publicKey.challenge = base64urlToBuffer(publicKey.challenge);
  if (publicKey.allowCredentials) {
    publicKey.allowCredentials = publicKey.allowCredentials.map((cred) => ({
      ...cred,
      id: base64urlToBuffer(cred.id),
    }));
  }

  // 3. Process extensions
  const extensionsAfterProcessing = invokeExtensionFunctions(publicKey.extensions);

  // 4. Call WebAuthn
  const assertion = await navigator.credentials.get({
    publicKey: publicKey,
  });

  if (!assertion) {
    throw new Error('Credential assertion failed or was cancelled.');
  }

  // 5. Prepare and send final assertion
  const assertionPayload = prepareAuthenticationAssertionPayload(
    assertion,
    extensionsAfterProcessing,
  );

  // 6. Call RP backend to complete authentication
  return await completeAuthentication({ assertion: assertionPayload, challenge_token });
}
