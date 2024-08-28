// Tree
const trees = document.querySelectorAll('.tree');

if (trees) {
  Array.from(trees).forEach((treeDOM) => {
    const tree = new eds.Tree(treeDOM);
    tree.init();
  });
}

// Layout & Page
const bodyDOM = document.querySelector('body');
const layout = new eds.Layout(bodyDOM);
const page = new eds.Page(bodyDOM);
page.init();
layout.init();

// Switch theme
document.querySelector('#switch-button').addEventListener('change', (event) => {
  let bodyClassList = document.body.classList;
  let theme = bodyClassList.value.includes('light') ? 'dark' : 'light';
  const switchThemeEvent = new CustomEvent('switchTheme', { detail: {theme: theme} });
  document.dispatchEvent(switchThemeEvent);
}, false);

// Dropdowns
const dropdowns = document.querySelectorAll('.dropdown');
if (dropdowns) {
  Array.from(dropdowns).forEach(dropdownDOM => {
    const dropdown = new eds.Dropdown(dropdownDOM);
    dropdown.init();
  });
}

const selects = document.querySelectorAll('.select');

if (selects) {
  Array.from(selects).forEach((selectDOM) => {
    const select = new eds.Select(selectDOM);
    select.init();
  });
}


const accordions = document.querySelectorAll('.accordion');

if (accordions) {
  Array.from(accordions).forEach((accordionDOM) => {
    const accordion = new eds.Accordion(accordionDOM);
    accordion.init();
  });
}


