import { registerPasskey } from './register.js';
import { authenticateWithPasskey } from './auth.js';
import { initDevLogger, devLog } from './devLogger.js';

devLog('info', 'App started');

const UsernameSessionKey = 'username';

// UI helpers
const outputElement = document.querySelector('#output');
const setOutput = (msg) => {
  if (outputElement) outputElement.textContent = msg;
};
const getErrorMessage = (err) =>
  `❌ Error: ${err?.response?.data?.detail || err.message || 'Unknown error'}`;

initDevLogger();

// Generic async wrapper to reduce duplication
async function runWithFeedback(action, successMessage, onSuccess) {
  try {
    const result = await action();
    if (onSuccess) {
      devLog('info', 'Operation succeeded:', result);
      onSuccess(result);
    }
    setOutput(successMessage);
  } catch (err) {
    console.error(err);
    devLog('error', 'Operation failed:', err);
    setOutput(getErrorMessage(err));
  }
}

export async function handleRegister(event) {
  event.preventDefault();
  const form = event.target;
  const username = form.username?.value.trim();

  if (username) {
    document.querySelectorAll('.username').forEach((el) => (el.value = username));
  }

  if (!username) {
    setOutput('⚠️ Username is required. Please enter a username.');
    return;
  }
  devLog('info', 'Calling registration with username:', username);

  await runWithFeedback(
    () => registerPasskey(username),
    '✅ Registered successfully.',
    () => sessionStorage.setItem(UsernameSessionKey, username),
  );
}

export async function handleAuthenticate(event) {
  event.preventDefault();
  const username = sessionStorage.getItem(UsernameSessionKey);

  if (!username) {
    setOutput('⚠️ Username is required. Please register first.');
    return;
  }

  devLog('info', 'Calling authentication with username:', username);

  await runWithFeedback(() => authenticateWithPasskey(username), '✅ Authentication successful.');
}

const handlers = {
  register: handleRegister,
  authenticate: handleAuthenticate,
};

document.querySelectorAll('form[data-action]').forEach((form) => {
  const action = form.dataset.action;
  const handler = handlers[action];

  if (handler) {
    form.addEventListener('submit', handler);
  } else {
    console.warn(`❌ No handler defined for action: ${action}`);
  }
});
