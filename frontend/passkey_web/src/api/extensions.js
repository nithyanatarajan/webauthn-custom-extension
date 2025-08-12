// src/api/extensions.js

import { postJson } from './utils.js';

const extnBase = import.meta.env.VITE_EXTN_BASE_URL;

export async function callExtension(path, payload = {}) {
  const res = await postJson(`${extnBase}/${path}`, payload);
  if (!res.ok) {
    const { detail } = await res.json();
    throw new Error(`Call failed: ${detail}`);
  }
  return res.json();
}
