const titles = {
  targets: ["Targets", "Configure and choose execution backends"],
  scenarios: ["Scenarios", "Review attack cases and expected safe behavior"],
  runs: ["Runs", "Inspect live and historical execution outcomes"],
  reports: ["Reports / Analysis", "Open generated markdown assessments"],
};

const navItems = Array.from(document.querySelectorAll(".nav-item"));
const views = {
  targets: document.getElementById("view-targets"),
  scenarios: document.getElementById("view-scenarios"),
  runs: document.getElementById("view-runs"),
  reports: document.getElementById("view-reports"),
};

const titleEl = document.getElementById("view-title");
const subtitleEl = document.getElementById("view-subtitle");

function selectView(name) {
  navItems.forEach((item) => item.classList.toggle("is-active", item.dataset.view === name));
  Object.entries(views).forEach(([key, element]) => {
    element.classList.toggle("is-visible", key === name);
  });

  const [title, subtitle] = titles[name];
  titleEl.textContent = title;
  subtitleEl.textContent = subtitle;
}

navItems.forEach((item) => {
  item.addEventListener("click", () => selectView(item.dataset.view));
});
