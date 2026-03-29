const titles = {
  targets: ["Targets", "Configure and choose execution backends"],
  scenarios: ["Scenarios", "Review attack cases and expected safe behavior"],
  runs: ["Runs", "Inspect live and historical execution outcomes"],
  reports: ["Reports / Analysis", "Open generated markdown assessments"],
};

const state = {
  selectedTarget: "local-mock",
  selectedScenarioId: null,
  selectedRunId: null,
  runs: [],
};

const views = {
  targets: document.getElementById("view-targets"),
  scenarios: document.getElementById("view-scenarios"),
  runs: document.getElementById("view-runs"),
  reports: document.getElementById("view-reports"),
};

const navItems = Array.from(document.querySelectorAll(".nav-item"));
const viewTitle = document.getElementById("view-title");
const viewSubtitle = document.getElementById("view-subtitle");

const targetSelect = document.getElementById("target-select");
const refreshBtn = document.getElementById("refresh-btn");

const targetsTableBody = document.querySelector("#targets-table tbody");
const scenariosTableBody = document.querySelector("#scenarios-table tbody");
const runsTableBody = document.querySelector("#runs-table tbody");

const runSelectedScenarioBtn = document.getElementById("run-selected-scenario-btn");

const detailScenario = document.getElementById("detail-scenario");
const detailVerdict = document.getElementById("detail-verdict");
const detailToolsBody = document.querySelector("#detail-tools-table tbody");
const detailViolationsBody = document.querySelector("#detail-violations-table tbody");
const detailTraceBody = document.querySelector("#detail-trace-table tbody");

const reportRunSelect = document.getElementById("report-run-select");
const loadReportBtn = document.getElementById("load-report-btn");
const downloadReportLink = document.getElementById("download-report-link");
const reportContent = document.getElementById("report-content");

refreshBtn.addEventListener("click", () => refreshAll());
runSelectedScenarioBtn.addEventListener("click", () => executeSelectedScenario());
loadReportBtn.addEventListener("click", () => loadSelectedReport());

navItems.forEach((item) => {
  item.addEventListener("click", () => selectView(item.dataset.view));
});

targetSelect.addEventListener("change", async () => {
  await postJson("/api/targets/select", { name: targetSelect.value });
  state.selectedTarget = targetSelect.value;
  await refreshRuns();
});

reportRunSelect.addEventListener("change", () => {
  const runId = reportRunSelect.value;
  downloadReportLink.href = runId ? `/api/reports/${runId}/download` : "#";
});

async function refreshAll() {
  await Promise.all([refreshTargets(), refreshScenarios(), refreshRuns()]);
}

function selectView(name) {
  navItems.forEach((item) => item.classList.toggle("is-active", item.dataset.view === name));
  Object.entries(views).forEach(([key, element]) => {
    element.classList.toggle("is-visible", key === name);
  });

  const [title, subtitle] = titles[name];
  viewTitle.textContent = title;
  viewSubtitle.textContent = subtitle;
}

async function refreshTargets() {
  const data = await getJson("/api/targets");
  const { targets, selected_target: selectedTarget } = data;

  state.selectedTarget = selectedTarget;
  targetSelect.innerHTML = targets
    .map((target) => `<option value="${escapeHtml(target.name)}">${escapeHtml(target.name)}</option>`)
    .join("");
  targetSelect.value = selectedTarget;

  targetsTableBody.innerHTML = targets
    .map(
      (target) => `
      <tr>
        <td>${escapeHtml(target.name)}</td>
        <td>${escapeHtml(target.type)}</td>
        <td>${statusBadge(target.status)}</td>
        <td>${escapeHtml(target.description || "")}</td>
      </tr>
    `
    )
    .join("");
}

async function refreshScenarios() {
  const data = await getJson("/api/scenarios");
  const scenarios = data.scenarios || [];

  if (!state.selectedScenarioId && scenarios.length > 0) {
    state.selectedScenarioId = scenarios[0].id;
  }

  scenariosTableBody.innerHTML = scenarios
    .map((scenario) => {
      const checked = scenario.id === state.selectedScenarioId ? "checked" : "";
      const focus = (scenario.security_focus || []).join(", ");
      const expected = (scenario.expected_behavior || [])
        .map((item) => `${item.rule_id} ${item.outcome}`)
        .join("; ");

      return `
        <tr>
          <td>
            <input type="radio" name="scenario-select" value="${escapeHtml(scenario.id)}" ${checked} />
          </td>
          <td>${escapeHtml(scenario.id)}</td>
          <td>${escapeHtml(scenario.title)}</td>
          <td>${escapeHtml(scenario.category)}</td>
          <td>${escapeHtml(focus)}</td>
          <td>${escapeHtml(expected)}</td>
        </tr>
      `;
    })
    .join("");

  document.querySelectorAll('input[name="scenario-select"]').forEach((node) => {
    node.addEventListener("change", () => {
      state.selectedScenarioId = node.value;
    });
  });
}

async function refreshRuns() {
  const data = await getJson("/api/runs");
  const runs = data.runs || [];
  state.runs = runs;

  runsTableBody.innerHTML = runs
    .map(
      (run) => `
      <tr>
        <td>${statusBadge(run.status)}</td>
        <td>${escapeHtml(run.target || state.selectedTarget)}</td>
        <td>${escapeHtml(run.scenario_id)} - ${escapeHtml(run.scenario_title || "")}</td>
        <td>${escapeHtml(formatTimestamp(run.timestamp))}</td>
        <td>${statusBadge(run.verdict)}</td>
        <td>${escapeHtml(run.analysis_state)}</td>
        <td>
          <button class="btn btn-ghost" data-action="view" data-run-id="${escapeHtml(run.run_id)}">View</button>
          <button class="btn btn-ghost" data-action="analyze" data-run-id="${escapeHtml(run.run_id)}">Analyze</button>
          <a class="btn btn-ghost" href="/api/reports/${encodeURIComponent(run.run_id)}/download">Download</a>
        </td>
      </tr>
    `
    )
    .join("");

  reportRunSelect.innerHTML = runs
    .map((run) => `<option value="${escapeHtml(run.run_id)}">${escapeHtml(run.run_id)}</option>`)
    .join("");

  if (runs.length > 0) {
    const firstRunId = runs[0].run_id;
    if (!state.selectedRunId || !runs.some((item) => item.run_id === state.selectedRunId)) {
      state.selectedRunId = firstRunId;
    }
    reportRunSelect.value = state.selectedRunId;
    downloadReportLink.href = `/api/reports/${encodeURIComponent(state.selectedRunId)}/download`;
  } else {
    state.selectedRunId = null;
    reportRunSelect.innerHTML = "";
    downloadReportLink.href = "#";
    clearRunDetail();
  }

  document.querySelectorAll("[data-action='view'], [data-action='analyze']").forEach((node) => {
    node.addEventListener("click", async () => {
      const runId = node.getAttribute("data-run-id");
      await showRunDetail(runId);
      if (node.getAttribute("data-action") === "analyze") {
        selectView("reports");
        reportRunSelect.value = runId;
        state.selectedRunId = runId;
        await loadReport(runId);
      }
    });
  });

  if (state.selectedRunId) {
    await showRunDetail(state.selectedRunId);
  }
}

async function executeSelectedScenario() {
  if (!state.selectedScenarioId) {
    alert("Select a scenario first.");
    return;
  }

  runSelectedScenarioBtn.disabled = true;
  runSelectedScenarioBtn.textContent = "Running...";

  try {
    const result = await postJson("/api/runs/execute", {
      scenario_id: state.selectedScenarioId,
      target: state.selectedTarget,
      max_steps: 8,
    });

    state.selectedRunId = result.run_id;
    await refreshRuns();
    selectView("runs");
  } catch (error) {
    alert(`Run failed: ${error.message}`);
  } finally {
    runSelectedScenarioBtn.disabled = false;
    runSelectedScenarioBtn.textContent = "Run Selected Scenario";
  }
}

async function showRunDetail(runId) {
  if (!runId) {
    clearRunDetail();
    return;
  }

  const detail = await getJson(`/api/runs/${encodeURIComponent(runId)}`);
  state.selectedRunId = runId;

  const scenario = detail.scenario || {};
  detailScenario.innerHTML = `
    <p><strong>ID:</strong> ${escapeHtml(scenario.id || "")}</p>
    <p><strong>Title:</strong> ${escapeHtml(scenario.title || "")}</p>
    <p><strong>Category:</strong> ${escapeHtml(scenario.category || "")}</p>
  `;

  if (detail.evaluation) {
    const evalData = detail.evaluation;
    detailVerdict.innerHTML = `
      <p><strong>Verdict:</strong> ${statusBadge(evalData.verdict)}</p>
      <p><strong>Overall Score:</strong> ${evalData.scores.overall_score}</p>
      <p><strong>Violations:</strong> ${evalData.violation_count}</p>
    `;
  } else {
    detailVerdict.innerHTML = "<p class='muted'>No evaluation available.</p>";
  }

  const toolCalls = detail.tool_calls || [];
  detailToolsBody.innerHTML = toolCalls
    .map(
      (item) => `
      <tr>
        <td>${item.step_index}</td>
        <td>${escapeHtml(item.tool || "")}</td>
        <td><span class="code">${escapeHtml(JSON.stringify(item.arguments || {}, null, 2))}</span></td>
      </tr>
    `
    )
    .join("");
  if (!toolCalls.length) {
    detailToolsBody.innerHTML = "<tr><td colspan='3' class='muted'>No tool calls.</td></tr>";
  }

  const violations = detail.violations || [];
  detailViolationsBody.innerHTML = violations
    .map(
      (item) => `
      <tr>
        <td>${escapeHtml(item.rule_id || "")}</td>
        <td>${escapeHtml(item.severity || "")}</td>
        <td>${escapeHtml(item.action || "")}</td>
        <td>${escapeHtml(item.message || "")}</td>
      </tr>
    `
    )
    .join("");
  if (!violations.length) {
    detailViolationsBody.innerHTML = "<tr><td colspan='4' class='muted'>No violations.</td></tr>";
  }

  const trace = detail.trace || [];
  detailTraceBody.innerHTML = trace
    .map(
      (event) => `
      <tr>
        <td>${event.step_index}</td>
        <td>${escapeHtml(formatTimestamp(event.timestamp))}</td>
        <td>${escapeHtml(event.event_type || "")}</td>
        <td><span class="code">${escapeHtml(JSON.stringify(event.payload || {}, null, 2))}</span></td>
      </tr>
    `
    )
    .join("");
  if (!trace.length) {
    detailTraceBody.innerHTML = "<tr><td colspan='4' class='muted'>No trace events.</td></tr>";
  }
}

function clearRunDetail() {
  detailScenario.innerHTML = "<p class='muted'>No run selected.</p>";
  detailVerdict.innerHTML = "<p class='muted'>No run selected.</p>";
  detailToolsBody.innerHTML = "<tr><td colspan='3' class='muted'>No tool calls.</td></tr>";
  detailViolationsBody.innerHTML = "<tr><td colspan='4' class='muted'>No violations.</td></tr>";
  detailTraceBody.innerHTML = "<tr><td colspan='4' class='muted'>No trace events.</td></tr>";
}

async function loadSelectedReport() {
  const runId = reportRunSelect.value;
  if (!runId) {
    return;
  }
  state.selectedRunId = runId;
  await loadReport(runId);
}

async function loadReport(runId) {
  const markdown = await fetchText(`/api/reports/${encodeURIComponent(runId)}`);
  reportContent.innerHTML = renderMarkdown(markdown);
  downloadReportLink.href = `/api/reports/${encodeURIComponent(runId)}/download`;
}

function statusBadge(value) {
  const normalized = String(value || "unknown").toLowerCase();
  let cls = "badge-neutral";
  if (normalized.includes("running")) cls = "badge-running";
  else if (normalized.includes("pass")) cls = "badge-success";
  else if (normalized.includes("warning") || normalized.includes("pending")) cls = "badge-warning";
  else if (normalized.includes("fail") || normalized.includes("stopped") || normalized.includes("critical")) cls = "badge-critical";
  return `<span class="badge ${cls}">${escapeHtml(String(value || "unknown"))}</span>`;
}

function renderMarkdown(markdown) {
  const lines = markdown.split(/\r?\n/);
  const html = [];
  let i = 0;

  while (i < lines.length) {
    const line = lines[i];

    if (line.startsWith("### ")) {
      html.push(`<h3>${escapeHtml(line.slice(4))}</h3>`);
      i += 1;
      continue;
    }
    if (line.startsWith("## ")) {
      html.push(`<h2>${escapeHtml(line.slice(3))}</h2>`);
      i += 1;
      continue;
    }
    if (line.startsWith("# ")) {
      html.push(`<h1>${escapeHtml(line.slice(2))}</h1>`);
      i += 1;
      continue;
    }

    if (line.startsWith("|")) {
      const tableLines = [];
      while (i < lines.length && lines[i].startsWith("|")) {
        tableLines.push(lines[i]);
        i += 1;
      }
      html.push(renderTable(tableLines));
      continue;
    }

    if (line.startsWith("- ")) {
      const items = [];
      while (i < lines.length && lines[i].startsWith("- ")) {
        items.push(lines[i].slice(2));
        i += 1;
      }
      html.push(`<ul>${items.map((item) => `<li>${escapeHtml(item)}</li>`).join("")}</ul>`);
      continue;
    }

    if (line.trim() === "") {
      i += 1;
      continue;
    }

    html.push(`<p>${escapeHtml(line)}</p>`);
    i += 1;
  }

  return html.join("\n");
}

function renderTable(tableLines) {
  if (tableLines.length < 2) {
    return `<pre class="code">${escapeHtml(tableLines.join("\n"))}</pre>`;
  }

  const rows = tableLines
    .map((line) => line.split("|").slice(1, -1).map((cell) => cell.trim()))
    .filter((cells) => cells.length > 0);

  if (rows.length < 2) {
    return `<pre class="code">${escapeHtml(tableLines.join("\n"))}</pre>`;
  }

  const header = rows[0];
  const body = rows.slice(2);

  return `
    <table>
      <thead>
        <tr>${header.map((cell) => `<th>${escapeHtml(cell)}</th>`).join("")}</tr>
      </thead>
      <tbody>
        ${body.map((row) => `<tr>${row.map((cell) => `<td>${escapeHtml(cell)}</td>`).join("")}</tr>`).join("")}
      </tbody>
    </table>
  `;
}

function formatTimestamp(value) {
  if (!value) return "";
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return value;
  return date.toLocaleString();
}

function escapeHtml(text) {
  return String(text)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/\"/g, "&quot;")
    .replace(/'/g, "&#039;");
}

async function getJson(url) {
  const response = await fetch(url);
  if (!response.ok) {
    const text = await response.text();
    throw new Error(text || response.statusText);
  }
  return response.json();
}

async function postJson(url, payload) {
  const response = await fetch(url, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  if (!response.ok) {
    const text = await response.text();
    throw new Error(text || response.statusText);
  }
  return response.json();
}

async function fetchText(url) {
  const response = await fetch(url);
  if (!response.ok) {
    const text = await response.text();
    throw new Error(text || response.statusText);
  }
  return response.text();
}

refreshAll().catch((error) => {
  reportContent.innerHTML = `<p class="muted">UI initialization failed: ${escapeHtml(error.message)}</p>`;
});
