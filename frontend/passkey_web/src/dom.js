// src/dom.js
export function initTabs(root = document) {
  const tabs = root.querySelectorAll('.tab-button');
  const contents = root.querySelectorAll('.tab-content');

  tabs.forEach((tab) => {
    tab.addEventListener('click', () => {
      tabs.forEach((t) => t.classList.remove('active'));
      contents.forEach((c) => c.classList.remove('active'));

      tab.classList.add('active');
      const target = root.querySelector(tab.dataset.target);
      if (target) target.classList.add('active');
    });
  });

  if (tabs.length > 0) {
    tabs[0].click();
  }
}
