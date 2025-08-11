import { base64urlToBuffer, prepareAuthenticationAssertionPayload } from './utils.js';

export async function authenticateWithPasskey(username) {
  const apiBase = import.meta.env.VITE_API_BASE_URL;

  // 1. Begin authentication
  const res = await fetch(`${apiBase}/authenticate/begin`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ username }),
  });

  if (!res.ok) {
    const { detail } = await res.json();
    throw new Error(`Authentication begin failed: ${detail}`);
  }

  const { publicKey, challenge_token } = await res.json();

  // 2. Convert to ArrayBuffers
  publicKey.challenge = base64urlToBuffer(publicKey.challenge);
  if (publicKey.allowCredentials) {
    publicKey.allowCredentials = publicKey.allowCredentials.map((cred) => ({
      ...cred,
      id: base64urlToBuffer(cred.id),
    }));
  }

  // 3. Call WebAuthn
  const assertion = await navigator.credentials.get({
    publicKey: publicKey,
  });

  if (!assertion) {
    throw new Error('Credential assertion failed or was cancelled.');
  }

  // 4. Prepare and send final assertion
  const assertionPayload = prepareAuthenticationAssertionPayload(assertion);

  const finalRes = await fetch(`${apiBase}/authenticate/complete`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ assertion: assertionPayload, challenge_token }),
  });

  if (!finalRes.ok) {
    const { detail } = await finalRes.json();
    throw new Error(`Authentication complete failed: ${detail}`);
  }

  return await finalRes.json();
}
