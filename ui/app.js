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
  replay: null,
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
const replayPrevBtn = document.getElementById("replay-prev-btn");
const replayNextBtn = document.getElementById("replay-next-btn");
const replayPlayBtn = document.getElementById("replay-play-btn");
const replayPosition = document.getElementById("replay-position");
const replayCurrentEvent = document.getElementById("replay-current-event");

const reportRunSelect = document.getElementById("report-run-select");
const loadReportBtn = document.getElementById("load-report-btn");
const downloadReportLink = document.getElementById("download-report-link");
const downloadJsonLink = document.getElementById("download-json-link");
const downloadPdfLink = document.getElementById("download-pdf-link");
const downloadBundleLink = document.getElementById("download-bundle-link");
const reportContent = document.getElementById("report-content");
const compareLeftRunSelect = document.getElementById("compare-left-run-select");
const compareRightRunSelect = document.getElementById("compare-right-run-select");
const compareRunsBtn = document.getElementById("compare-runs-btn");
const compareContent = document.getElementById("compare-content");
const differentialScenarioSelect = document.getElementById("differential-scenario-select");
const runDifferentialBtn = document.getElementById("run-differential-btn");
const differentialContent = document.getElementById("differential-content");

refreshBtn.addEventListener("click", () => refreshAll());
runSelectedScenarioBtn.addEventListener("click", () => executeSelectedScenario());
loadReportBtn.addEventListener("click", () => loadSelectedReport());
compareRunsBtn.addEventListener("click", () => compareSelectedRuns());
runDifferentialBtn.addEventListener("click", () => runDifferentialForScenario());
replayPrevBtn.addEventListener("click", () => handleReplayPrev());
replayNextBtn.addEventListener("click", () => handleReplayNext());
replayPlayBtn.addEventListener("click", () => toggleReplayPlayback());

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
  if (!runId) {
    downloadReportLink.href = "#";
    downloadJsonLink.href = "#";
    downloadPdfLink.href = "#";
    downloadBundleLink.href = "#";
    return;
  }
  updateArtifactLinks(runId);
});

let replayTimer = null;

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
  compareLeftRunSelect.innerHTML = runs
    .map((run) => `<option value="${escapeHtml(run.run_id)}">${escapeHtml(run.run_id)}</option>`)
    .join("");
  compareRightRunSelect.innerHTML = runs
    .map((run) => `<option value="${escapeHtml(run.run_id)}">${escapeHtml(run.run_id)}</option>`)
    .join("");
  const scenarioIds = Array.from(new Set(runs.map((run) => run.scenario_id))).sort();
  differentialScenarioSelect.innerHTML = scenarioIds
    .map((scenarioId) => `<option value="${escapeHtml(scenarioId)}">${escapeHtml(scenarioId)}</option>`)
    .join("");

  if (runs.length > 0) {
    const firstRunId = runs[0].run_id;
    const secondRunId = (runs[1] || runs[0]).run_id;
    if (!state.selectedRunId || !runs.some((item) => item.run_id === state.selectedRunId)) {
      state.selectedRunId = firstRunId;
    }
    reportRunSelect.value = state.selectedRunId;
    compareLeftRunSelect.value = firstRunId;
    compareRightRunSelect.value = secondRunId;
    if (scenarioIds.length > 0) {
      differentialScenarioSelect.value = scenarioIds[0];
    }
    updateArtifactLinks(state.selectedRunId);
  } else {
    state.selectedRunId = null;
    reportRunSelect.innerHTML = "";
    compareLeftRunSelect.innerHTML = "";
    compareRightRunSelect.innerHTML = "";
    differentialScenarioSelect.innerHTML = "";
    downloadReportLink.href = "#";
    downloadJsonLink.href = "#";
    downloadPdfLink.href = "#";
    downloadBundleLink.href = "#";
    compareContent.innerHTML = "<p class='muted'>Select two runs and click Compare Runs.</p>";
    differentialContent.innerHTML = "<p class='muted'>Select a scenario and click Run Differential.</p>";
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

  await loadReplay(runId, 0);
}

function clearRunDetail() {
  stopReplayPlayback();
  state.replay = null;
  detailScenario.innerHTML = "<p class='muted'>No run selected.</p>";
  detailVerdict.innerHTML = "<p class='muted'>No run selected.</p>";
  detailToolsBody.innerHTML = "<tr><td colspan='3' class='muted'>No tool calls.</td></tr>";
  detailViolationsBody.innerHTML = "<tr><td colspan='4' class='muted'>No violations.</td></tr>";
  detailTraceBody.innerHTML = "<tr><td colspan='4' class='muted'>No trace events.</td></tr>";
  replayPosition.textContent = "event 0 / 0";
  replayCurrentEvent.innerHTML = "<p class='muted'>Select a run to replay trace events.</p>";
  replayPrevBtn.disabled = true;
  replayNextBtn.disabled = true;
  replayPlayBtn.disabled = true;
  replayPlayBtn.textContent = "Play";
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
  updateArtifactLinks(runId);
}

async function compareSelectedRuns() {
  const leftRunId = compareLeftRunSelect.value;
  const rightRunId = compareRightRunSelect.value;

  if (!leftRunId || !rightRunId) {
    compareContent.innerHTML = "<p class='muted'>Select two runs to compare.</p>";
    return;
  }

  const comparison = await getJson(
    `/api/runs/compare?left=${encodeURIComponent(leftRunId)}&right=${encodeURIComponent(rightRunId)}`
  );
  compareContent.innerHTML = renderComparison(comparison);
}

function renderComparison(comparison) {
  const left = comparison.left || {};
  const right = comparison.right || {};
  const delta = comparison.delta || {};
  const violations = comparison.violations || {};
  const tools = comparison.tools || {};

  return `
    <h3>Run Comparison</h3>
    <table>
      <thead>
        <tr>
          <th>Metric</th>
          <th>Left</th>
          <th>Right</th>
          <th>Delta (right-left)</th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <td>Run ID</td>
          <td>${escapeHtml(left.run_id || "")}</td>
          <td>${escapeHtml(right.run_id || "")}</td>
          <td></td>
        </tr>
        <tr>
          <td>Scenario</td>
          <td>${escapeHtml(left.scenario_id || "")}</td>
          <td>${escapeHtml(right.scenario_id || "")}</td>
          <td></td>
        </tr>
        <tr>
          <td>Status</td>
          <td>${statusBadge(left.status)}</td>
          <td>${statusBadge(right.status)}</td>
          <td></td>
        </tr>
        <tr>
          <td>Verdict</td>
          <td>${statusBadge(left.verdict)}</td>
          <td>${statusBadge(right.verdict)}</td>
          <td></td>
        </tr>
        <tr>
          <td>Overall score</td>
          <td>${escapeHtml(String(left.overall_score ?? "n/a"))}</td>
          <td>${escapeHtml(String(right.overall_score ?? "n/a"))}</td>
          <td>${escapeHtml(String(delta.overall_score ?? "n/a"))}</td>
        </tr>
        <tr>
          <td>Violation count</td>
          <td>${escapeHtml(String(left.violation_count ?? 0))}</td>
          <td>${escapeHtml(String(right.violation_count ?? 0))}</td>
          <td>${escapeHtml(String(delta.violation_count ?? 0))}</td>
        </tr>
      </tbody>
    </table>
    <p><strong>New violations in right:</strong> ${escapeHtml((violations.new_in_right || []).join(", ") || "none")}</p>
    <p><strong>Resolved in right:</strong> ${escapeHtml((violations.resolved_in_right || []).join(", ") || "none")}</p>
    <p><strong>New tools in right:</strong> ${escapeHtml((tools.new_in_right || []).join(", ") || "none")}</p>
    <p><strong>Missing tools in right:</strong> ${escapeHtml((tools.missing_in_right || []).join(", ") || "none")}</p>
  `;
}

async function runDifferentialForScenario() {
  const scenarioId = differentialScenarioSelect.value;
  if (!scenarioId) {
    differentialContent.innerHTML = "<p class='muted'>Select a scenario to run differential testing.</p>";
    return;
  }

  const data = await getJson(`/api/differential/${encodeURIComponent(scenarioId)}`);
  differentialContent.innerHTML = renderDifferential(data);
}

function renderDifferential(data) {
  const models = data.models || [];
  const divergentRules = data.divergent_rule_ids || [];

  if (!models.length) {
    return "<p class='muted'>No differential data available.</p>";
  }

  return `
    <h3>Differential Summary</h3>
    <p><strong>Scenario:</strong> ${escapeHtml(data.scenario_id || "")}</p>
    <p><strong>Models Compared:</strong> ${escapeHtml(String(data.model_count || 0))}</p>
    <p><strong>Consensus Verdict:</strong> ${statusBadge(data.consensus_verdict)}</p>
    <p><strong>Score Spread:</strong> ${escapeHtml(String(data.score_spread ?? "n/a"))}</p>
    <p><strong>Divergent Rules:</strong> ${escapeHtml(divergentRules.join(", ") || "none")}</p>
    <table>
      <thead>
        <tr>
          <th>Model</th>
          <th>Target</th>
          <th>Run ID</th>
          <th>Status</th>
          <th>Verdict</th>
          <th>Score</th>
          <th>Violations</th>
          <th>Rule IDs</th>
        </tr>
      </thead>
      <tbody>
        ${models
          .map(
            (row) => `
          <tr>
            <td>${escapeHtml(row.model_label || "")}</td>
            <td>${escapeHtml(row.target || "")}</td>
            <td>${escapeHtml(row.run_id || "")}</td>
            <td>${statusBadge(row.status)}</td>
            <td>${statusBadge(row.verdict)}</td>
            <td>${escapeHtml(String(row.overall_score ?? "n/a"))}</td>
            <td>${escapeHtml(String(row.violation_count ?? 0))}</td>
            <td>${escapeHtml((row.rule_ids || []).join(", ") || "none")}</td>
          </tr>
        `
          )
          .join("")}
      </tbody>
    </table>
  `;
}

function updateArtifactLinks(runId) {
  const encodedRunId = encodeURIComponent(runId);
  downloadReportLink.href = `/api/reports/${encodedRunId}/download`;
  downloadJsonLink.href = `/api/exports/${encodedRunId}.json`;
  downloadPdfLink.href = `/api/exports/${encodedRunId}.pdf`;
  downloadBundleLink.href = `/api/exports/${encodedRunId}.zip`;
}

async function loadReplay(runId, index) {
  const replay = await getJson(`/api/runs/${encodeURIComponent(runId)}/replay?index=${index}`);
  state.replay = replay;
  renderReplay(replay);
}

function renderReplay(replay) {
  const total = replay.total_events || 0;
  const index = replay.index || 0;
  replayPosition.textContent = `event ${total ? index + 1 : 0} / ${total}`;

  if (!replay.current_event) {
    replayCurrentEvent.innerHTML = "<p class='muted'>No trace events available.</p>";
    replayPrevBtn.disabled = true;
    replayNextBtn.disabled = true;
    replayPlayBtn.disabled = true;
    replayPlayBtn.textContent = "Play";
    return;
  }

  const event = replay.current_event;
  replayCurrentEvent.innerHTML = `
    <p><strong>Step:</strong> ${escapeHtml(String(event.step_index))}</p>
    <p><strong>Timestamp:</strong> ${escapeHtml(formatTimestamp(event.timestamp))}</p>
    <p><strong>Event:</strong> ${escapeHtml(event.event_type || "")}</p>
    <p><strong>Payload:</strong></p>
    <pre class="code">${escapeHtml(JSON.stringify(event.payload || {}, null, 2))}</pre>
  `;

  replayPrevBtn.disabled = replay.previous_index == null;
  replayNextBtn.disabled = replay.next_index == null;
  replayPlayBtn.disabled = replay.next_index == null && replay.previous_index == null;
}

async function handleReplayPrev() {
  if (!state.selectedRunId || !state.replay || state.replay.previous_index == null) {
    return;
  }
  stopReplayPlayback();
  await loadReplay(state.selectedRunId, state.replay.previous_index);
}

async function handleReplayNext() {
  if (!state.selectedRunId || !state.replay || state.replay.next_index == null) {
    return;
  }
  await loadReplay(state.selectedRunId, state.replay.next_index);
}

function toggleReplayPlayback() {
  if (replayTimer) {
    stopReplayPlayback();
    return;
  }

  if (!state.selectedRunId || !state.replay || state.replay.next_index == null) {
    return;
  }

  replayPlayBtn.textContent = "Pause";
  replayTimer = setInterval(async () => {
    if (!state.replay || state.replay.next_index == null) {
      stopReplayPlayback();
      return;
    }
    await loadReplay(state.selectedRunId, state.replay.next_index);
  }, 800);
}

function stopReplayPlayback() {
  if (!replayTimer) {
    replayPlayBtn.textContent = "Play";
    return;
  }
  clearInterval(replayTimer);
  replayTimer = null;
  replayPlayBtn.textContent = "Play";
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
