// src/api/auth.js

import { postJson } from './utils.js';

const apiBase = import.meta.env.VITE_API_BASE_URL;

export async function beginAuthentication(username) {
  const res = await postJson(`${apiBase}/authenticate/begin`, { username });
  if (!res.ok) {
    const { detail } = await res.json();
    throw new Error(`Authentication begin failed: ${detail}`);
  }
  return res.json();
}

export async function completeAuthentication({ assertion, challenge_token }) {
  const res = await postJson(`${apiBase}/authenticate/complete`, { assertion, challenge_token });
  if (!res.ok) {
    const { detail } = await res.json();
    throw new Error(`Authentication complete failed: ${detail}`);
  }
  return res.json();
}
