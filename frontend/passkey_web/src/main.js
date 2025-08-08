const UsernameSessionKey = 'username';

export async function handleRegister(event) {
  event.preventDefault();
  const form = event.target;
  const username = form.username?.value.trim();
  const output = document.querySelector('#output');

  if (!username) {
    output.textContent = '⚠️ Username is required. Please enter a username.';
  }
}

export async function handleAuthenticate(event) {
  event.preventDefault();
  const form = event.target;
  const username = form.username?.value.trim() || sessionStorage.getItem(UsernameSessionKey);
  const output = document.querySelector('#output');

  if (!username) {
    output.textContent = '⚠️ Username is required. Please register first.';
  }
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
