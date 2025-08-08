import { initTabs } from './dom';

function mountDOM() {
  document.body.innerHTML = `
    <div class="tabs">
      <button class="tab-button" data-target="#register-tab">Register</button>
      <button class="tab-button" data-target="#authenticate-tab">Authenticate</button>
    </div>
    <div id="register-tab" class="tab-content">Register content</div>
    <div id="authenticate-tab" class="tab-content">Auth content</div>
  `;
}

test('initTabs sets first tab active by default', () => {
  mountDOM();
  initTabs(document);

  const tabs = document.querySelectorAll('.tab-button');
  const register = document.querySelector('#register-tab');
  const auth = document.querySelector('#authenticate-tab');

  expect(tabs[0].classList.contains('active')).toBe(true);
  expect(register.classList.contains('active')).toBe(true);
  expect(auth.classList.contains('active')).toBe(false);
});

test('clicking second tab switches active classes', async () => {
  mountDOM();
  initTabs(document);

  const tabs = document.querySelectorAll('.tab-button');
  const register = document.querySelector('#register-tab');
  const auth = document.querySelector('#authenticate-tab');

  tabs[1].click();

  expect(tabs[1].classList.contains('active')).toBe(true);
  expect(auth.classList.contains('active')).toBe(true);
  expect(register.classList.contains('active')).toBe(false);
});
