// register.js
import { base64urlToBuffer, prepareRegistrationAttestationPayload } from './utils.js';

function getBrowserType() {
  const test = regexp => {
    return regexp.test(navigator.userAgent);
  };

  if (test(/opr\//i) || !!window.opr) {
    return 'Opera';
  } else if (test(/edg/i)) {
    return 'Microsoft Edge';
  } else if (test(/chrome|chromium|crios/i)) {
    return 'Google Chrome';
  } else if (test(/firefox|fxios/i)) {
    return 'Mozilla Firefox';
  } else if (test(/safari/i)) {
    return 'Apple Safari';
  } else if (test(/trident/i)) {
    return 'Microsoft Internet Explorer';
  } else if (test(/ucbrowser/i)) {
    return 'UC Browser';
  } else if (test(/samsungbrowser/i)) {
    return 'Samsung Browser';
  } else {
    return 'Unknown browser';
  }
}

const customAuthMethods = {
  verifyBrowserIsGoogleChrome: () => {
    var browserType = getBrowserType();
    console.log(`Browser type detected: ${browserType}`);
    return browserType == 'Google Chrome';
  },
};

export async function registerPasskey(username) {
  const apiBase = import.meta.env.VITE_API_BASE_URL;

  // 1. Begin registration with RP backend
  const res = await fetch(`${apiBase}/register/begin`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ username }),
  });

  if (!res.ok) {
    const { detail } = await res.json();
    throw new Error(`Registration begin failed: ${detail}`);
  }

  const { publicKey, challenge_token } = await res.json();

  const methodName = publicKey.extensions.customAuthMethod;
  if (methodName && typeof customAuthMethods[methodName] === 'function') {
    if (!customAuthMethods[methodName]()) {
      throw new Error('Custom authentication failed');
    }
  }

  // 2. Convert challenge and user.id
  publicKey.challenge = base64urlToBuffer(publicKey.challenge);
  publicKey.user.id = base64urlToBuffer(publicKey.user.id);

  if (publicKey.excludeCredentials) {
    publicKey.excludeCredentials = publicKey.excludeCredentials.map((cred) => ({
      ...cred,
      id: base64urlToBuffer(cred.id),
    }));
  }

  // 3. Call WebAuthn API
  const credential = await navigator.credentials.create({
    publicKey: publicKey,
  });

  if (!credential) {
    throw new Error('Credential creation failed or was cancelled.');
  }

  // 4. Prepare attestation object
  const attestation = prepareRegistrationAttestationPayload(credential);
  const extensionResults = credential.getClientExtensionResults?.() || {};
  extensionResults.isBrowserGoogleChrome = customAuthMethods.verifyBrowserIsGoogleChrome();
  attestation.extensions = extensionResults;

  // 5. Call RP backend to complete registration
  const finishRes = await fetch(`${apiBase}/register/complete`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ attestation, challenge_token }),
  });

  if (!finishRes.ok) {
    const { detail } = await finishRes.json();
    throw new Error(`Registration complete failed: ${detail}`);
  }

  return await finishRes.json(); // if needed
}
