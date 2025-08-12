// src/api/register.js

import { postJson } from './utils.js';

const apiBase = import.meta.env.VITE_API_BASE_URL;

export async function beginRegistration(username) {
  const res = await postJson(`${apiBase}/register/begin`, { username });
  if (!res.ok) {
    const { detail } = await res.json();
    throw new Error(`Registration begin failed: ${detail}`);
  }
  return res.json();
}

export async function completeRegistration({ attestation, challenge_token }) {
  const res = await postJson(`${apiBase}/register/complete`, { attestation, challenge_token });
  if (!res.ok) {
    const { detail } = await res.json();
    throw new Error(`Registration complete failed: ${detail}`);
  }
  return res.json();
}
