const menuButton = document.querySelector(".menu-toggle");
const sidebar = document.querySelector(".sidebar");

if (menuButton && sidebar) {
  menuButton.addEventListener("click", () => {
    const expanded = menuButton.getAttribute("aria-expanded") === "true";
    menuButton.setAttribute("aria-expanded", String(!expanded));
    sidebar.classList.toggle("is-open", !expanded);
  });
}

if (window.hljs) {
  window.hljs.highlightAll();
}
