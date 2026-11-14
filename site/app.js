"use strict";

(() => {
  const REPOSITORY = "https://github.com/11ly322/causal-anchored-metacognitive-society";
  const FIXTURE_IDS = [
    "accept", "measurement", "insufficient", "fail-tampered-stdout-hash",
    "fail-replay-nonce", "fail-empty-checksum", "fail-no-tool"
  ];
  const STEP_NAMES = ["声明", "工具调用", "工具回执", "关联与溯源", "证据门控", "结果契约"];
  const OUTCOMES = {
    accept: { label: "可接受", style: "accept" },
    MEASUREMENT_FAILURE: { label: "测量失败", style: "measurement" },
    INSUFFICIENT_EVIDENCE: { label: "证据不足", style: "insufficient" }
  };
  const byId = (id) => document.getElementById(id);
  const panels = Array.from(document.querySelectorAll(".step-article"));
  const stepLinks = Array.from(document.querySelectorAll("[data-step]"));
  let activeStep = 0;
  let data = null;

  function setText(id, value) {
    byId(id).textContent = String(value);
  }

  function showStep(index, moveFocus = false) {
    activeStep = Math.max(0, Math.min(panels.length - 1, index));
    panels.forEach((panel, position) => { panel.hidden = position !== activeStep; });
    stepLinks.forEach((link, position) => {
      if (position === activeStep) link.setAttribute("aria-current", "step");
      else link.removeAttribute("aria-current");
    });
    byId("previous-step").disabled = activeStep === 0;
    byId("next-step").disabled = activeStep === panels.length - 1;
    byId("step-progress").value = activeStep + 1;
    setText("progress-text", `阅读进度 · ${activeStep + 1} / ${panels.length}`);
    setText("step-status", `第 ${activeStep + 1} 步，共 ${panels.length} 步：${STEP_NAMES[activeStep]}`);
    if (moveFocus) panels[activeStep].querySelector("h3").focus();
  }

  function stepFromHash() {
    const index = panels.findIndex((panel) => `#${panel.id}` === window.location.hash);
    if (index !== -1) showStep(index);
  }

  function initializeTour() {
    document.documentElement.classList.add("tour-enhanced");
    byId("tour-progress").hidden = false;
    byId("tour-controls").hidden = false;
    stepLinks.forEach((link, index) => {
      link.addEventListener("click", (event) => {
        event.preventDefault();
        showStep(index, true);
      });
    });
    byId("previous-step").addEventListener("click", () => showStep(activeStep - 1, true));
    byId("next-step").addEventListener("click", () => showStep(activeStep + 1, true));
    window.addEventListener("hashchange", stepFromHash);
    showStep(0);
    stepFromHash();
  }

  // This checks the presentation envelope, not receipt validity or gate decisions.
  // Invalid receipt content (including an empty hash) is evidence to display.
  function requireShape(condition, path) {
    if (!condition) throw new Error(`数据结构不符：${path}。`);
  }
  const isObject = (value) => value !== null && typeof value === "object" && !Array.isArray(value);
  const isString = (value) => typeof value === "string";
  const isText = (value) => isString(value) && value.length > 0;
  const isNumber = (value) => typeof value === "number" && Number.isFinite(value);
  const isInteger = (value) => Number.isSafeInteger(value);
  const isStrings = (value) => Array.isArray(value) && value.every(isString);
  const isDigest = (value) => isString(value) && /^sha256:[0-9a-f]{64}$/.test(value);

  function sameJSON(left, right) {
    if (left === right) return true;
    if (Array.isArray(left)) {
      return Array.isArray(right) && left.length === right.length &&
        left.every((value, index) => sameJSON(value, right[index]));
    }
    if (!isObject(left) || !isObject(right)) return false;
    const keys = Object.keys(left);
    return keys.length === Object.keys(right).length &&
      keys.every((key) => Object.prototype.hasOwnProperty.call(right, key) && sameJSON(left[key], right[key]));
  }

  function parseRecordedJSON(raw, path) {
    try { return JSON.parse(raw); }
    catch { throw new Error(`记录不是有效 JSON：${path}。`); }
  }

  function validateTrace(trace, path, fixtureId) {
    requireShape(isObject(trace), path);
    requireShape(trace.case === fixtureId && isText(trace.fixture_now), `${path}.case / fixture_now`);
    requireShape(isObject(trace.tool), `${path}.tool`);
    requireShape(isText(trace.tool.tool_id) && isInteger(trace.tool.exit_code) &&
      isString(trace.tool.stdout) && isStrings(trace.tool.args) &&
      (trace.tool.stdin === null || isString(trace.tool.stdin)), `${path}.tool 字段`);
    requireShape(Array.isArray(trace.receipts), `${path}.receipts`);
    trace.receipts.forEach((receipt, index) => {
      const itemPath = `${path}.receipts[${index}]`;
      requireShape(isObject(receipt), itemPath);
      ["receipt_id", "tool_id", "stdout_hash", "nonce", "timestamp", "signature", "input_digest"].forEach((key) => {
        requireShape(isString(receipt[key]), `${itemPath}.${key}`);
      });
      requireShape(isInteger(receipt.exit_code), `${itemPath}.exit_code`);
      if ("stderr_hash" in receipt) requireShape(isString(receipt.stderr_hash), `${itemPath}.stderr_hash`);
      if ("metadata" in receipt) requireShape(isObject(receipt.metadata), `${itemPath}.metadata`);
    });
    requireShape(Array.isArray(trace.claims) && trace.claims.length > 0, `${path}.claims`);
    trace.claims.forEach((claim, index) => {
      requireShape(isObject(claim) && isText(claim.claim_id) && isString(claim.text) &&
        isStrings(claim.evidence) && isString(claim.scope) && typeof claim.required === "boolean",
      `${path}.claims[${index}]`);
    });
    const policy = trace.policy;
    requireShape(isObject(policy) && policy.clock_mode === "fixture", `${path}.policy.clock_mode`);
    requireShape(isNumber(policy.min_coverage) && isNumber(policy.max_age_seconds) &&
      isNumber(policy.future_skew_seconds) && typeof policy.tool_required === "boolean" &&
      isStrings(policy.allowed_tools) && isStrings(policy.allowed_scopes) && isString(policy.trust_domain),
    `${path}.policy 字段`);
  }

  function validateContract(contract, path) {
    requireShape(isObject(contract), path);
    requireShape(contract.contract_version === "0.1", `${path}.contract_version`);
    requireShape(Object.prototype.hasOwnProperty.call(OUTCOMES, contract.decision), `${path}.decision`);
    requireShape(["NO_RISK", "MEASUREMENT_FAILURE", "INSUFFICIENT_EVIDENCE"].includes(contract.reason_code), `${path}.reason_code`);
    requireShape(contract.detail_code === null || isText(contract.detail_code), `${path}.detail_code`);
    requireShape(isNumber(contract.evidence_coverage) && contract.evidence_coverage >= 0 &&
      contract.evidence_coverage <= 1, `${path}.evidence_coverage`);
    requireShape(["none", "retry_tool", "human_review"].includes(contract.escalation_path), `${path}.escalation_path`);
    if ("message" in contract) requireShape(isString(contract.message), `${path}.message`);
    const provenance = contract.provenance_summary;
    requireShape(isObject(provenance) && Array.isArray(provenance.receipts), `${path}.provenance_summary`);
    requireShape(isInteger(provenance.verified_leaves) && provenance.verified_leaves >= 0 &&
      isInteger(provenance.required_leaves) && provenance.required_leaves >= 0, `${path}.provenance_summary 计数字段`);
    provenance.receipts.forEach((receipt, index) => {
      requireShape(isObject(receipt) && isString(receipt.receipt_id) &&
        isString(receipt.tool_id) && isString(receipt.stdout_hash), `${path}.provenance_summary.receipts[${index}]`);
    });
  }

  function validateData(payload) {
    requireShape(isObject(payload) && payload.schema_version === 1, "schema_version");
    const build = payload.build;
    requireShape(isObject(build) && isString(build.commit) && /^[0-9a-f]{40}$/.test(build.commit), "build.commit");
    requireShape(typeof build.dirty === "boolean" && build.verifier_path === "demo/run.py" &&
      isDigest(build.verifier_sha256) && isText(build.python_version), "build 字段");
    const evidence = payload.evidence;
    requireShape(isObject(evidence) && evidence.kind === "offline-fixture" &&
      evidence.clock_mode === "fixture" && evidence.live === false, "evidence");
    requireShape(Array.isArray(payload.fixtures) && payload.fixtures.length === FIXTURE_IDS.length, "fixtures（必须是七条记录）");
    payload.fixtures.forEach((fixture, index) => {
      const path = `fixtures[${index}]`;
      requireShape(isObject(fixture) && fixture.id === FIXTURE_IDS[index], `${path}.id / 顺序`);
      requireShape(isText(fixture.label) && isText(fixture.explanation), `${path}.label / explanation`);
      requireShape(fixture.source_path === `traces/${fixture.id}.json`, `${path}.source_path`);
      requireShape(fixture.source_url === `${REPOSITORY}/blob/${build.commit}/${fixture.source_path}`, `${path}.source_url（固定提交链接）`);
      requireShape(isDigest(fixture.source_sha256), `${path}.source_sha256`);
      requireShape(fixture.command === `python demo/run.py --trace ${fixture.source_path}`, `${path}.command`);
      requireShape(isInteger(fixture.exit_code) && fixture.exit_code >= 0 && fixture.exit_code <= 255, `${path}.exit_code`);
      requireShape(isString(fixture.stdout) && isString(fixture.stderr) && isString(fixture.trace_raw), `${path}.原始文本`);
      validateContract(fixture.contract, `${path}.contract`);
      validateTrace(fixture.trace, `${path}.trace`, fixture.id);
      requireShape(sameJSON(parseRecordedJSON(fixture.stdout, `${path}.stdout`), fixture.contract), `${path}.stdout 与 contract 不一致`);
      requireShape(sameJSON(parseRecordedJSON(fixture.trace_raw, `${path}.trace_raw`), fixture.trace), `${path}.trace_raw 与 trace 不一致`);
    });
    return payload;
  }

  function appendHeading(container, title) {
    const heading = document.createElement("h4");
    heading.textContent = title;
    container.append(heading);
  }

  function appendNote(container, text) {
    const paragraph = document.createElement("p");
    paragraph.className = "field-note";
    paragraph.textContent = text;
    container.append(paragraph);
  }

  function appendJSON(container, title, value) {
    if (title) appendHeading(container, title);
    const pre = document.createElement("pre");
    pre.tabIndex = 0;
    pre.setAttribute("aria-label", title || "完整 JSON 字段");
    const code = document.createElement("code");
    code.textContent = JSON.stringify(value, null, 2);
    pre.append(code);
    container.append(pre);
  }

  function appendFields(container, fields) {
    const list = document.createElement("dl");
    list.className = "field-list";
    fields.forEach(([name, value]) => {
      const term = document.createElement("dt");
      const description = document.createElement("dd");
      term.textContent = name;
      description.textContent = typeof value === "string" ? (value === "" ? '""（空字符串）' : value) : JSON.stringify(value);
      list.append(term, description);
    });
    container.append(list);
  }

  function renderTour(fixture) {
    const trace = fixture.trace;
    setText("tour-fixture-name", fixture.label);
    const claims = byId("claim-fields");
    claims.replaceChildren();
    trace.claims.forEach((claim, index) => {
      appendHeading(claims, `声明 ${index + 1}`);
      appendFields(claims, Object.entries(claim));
    });

    const tool = byId("tool-fields");
    tool.replaceChildren();
    appendFields(tool, Object.entries(trace.tool).filter(([key]) => key !== "stdout"));
    appendHeading(tool, "工具 stdout（trace 中的原文）");
    const toolOutput = document.createElement("pre");
    toolOutput.tabIndex = 0;
    toolOutput.setAttribute("aria-label", "trace 中记录的工具 stdout");
    const outputCode = document.createElement("code");
    outputCode.textContent = trace.tool.stdout;
    toolOutput.append(outputCode);
    tool.append(toolOutput);
    appendNote(tool, "此处保留字符串原文，包括字面反斜杠；工具记录存在并不等于有可用回执。");

    const receipts = byId("receipt-fields");
    receipts.replaceChildren();
    if (trace.receipts.length === 0) {
      appendNote(receipts, "这条输入的 receipts 是空数组 []。trace 仍含工具描述，但没有回执；这里保留输入的实际结构。");
      appendJSON(receipts, "完整 receipts", trace.receipts);
    } else {
      trace.receipts.forEach((receipt, index) => {
        appendHeading(receipts, `回执 ${index + 1} · 输入记录`);
        appendFields(receipts, Object.entries(receipt));
      });
    }

    const binding = byId("binding-fields");
    binding.replaceChildren();
    trace.claims.forEach((claim) => {
      appendHeading(binding, `声明 ${claim.claim_id} 的引用`);
      appendFields(binding, [["claim_id", claim.claim_id], ["evidence", claim.evidence], ["scope", claim.scope], ["required", claim.required]]);
    });
    appendFields(binding, [["allowed_scopes", trace.policy.allowed_scopes], ["trust_domain", trace.policy.trust_domain]]);
    appendJSON(binding, "记录的 provenance_summary", fixture.contract.provenance_summary);
    appendNote(binding, "这是 verifier 返回的完整摘要。verified_leaves、required_leaves 与 evidence_coverage 各自原样呈现，网页不由计数推算覆盖率。");

    const gate = byId("gate-fields");
    gate.replaceChildren();
    appendFields(gate, [["fixture_now", trace.fixture_now], ["clock_mode", trace.policy.clock_mode]]);
    appendJSON(gate, "输入的完整 policy（演示策略）", trace.policy);
    appendHeading(gate, "保存的最终返回值");
    appendFields(gate, [["decision", fixture.contract.decision], ["reason_code", fixture.contract.reason_code],
      ["detail_code", fixture.contract.detail_code], ["evidence_coverage", fixture.contract.evidence_coverage]]);
    if (Object.prototype.hasOwnProperty.call(fixture.contract, "message")) {
      appendFields(gate, [["message", fixture.contract.message]]);
    }
    appendNote(gate, "该输入的 min_coverage 是演示策略值，不是实证最优阈值。最终返回值不提供逐项检查轨迹，不能据此补全后续检查状态。");

    const contract = byId("contract-fields");
    contract.replaceChildren();
    appendJSON(contract, "verifier 返回的完整 contract", fixture.contract);
  }

  function renderFixture(index) {
    const fixture = data.fixtures[index];
    const outcome = OUTCOMES[fixture.contract.decision];
    renderTour(fixture);
    setText("record-title", fixture.label);
    setText("fixture-explanation", fixture.explanation);
    setText("decision-label", outcome.label);
    setText("decision-value", fixture.contract.decision);
    setText("detail-value", `detail_code: ${fixture.contract.detail_code === null ? "null" : fixture.contract.detail_code}`);
    byId("decision-box").dataset.outcome = outcome.style;
    setText("record-exit", fixture.exit_code);
    setText("record-coverage", fixture.contract.evidence_coverage);
    setText("record-escalation", fixture.contract.escalation_path);
    setText("fixture-path", fixture.source_path);
    setText("fixture-hash", fixture.source_sha256);
    byId("fixture-source").href = fixture.source_url;
    setText("reproduction-command", fixture.command);
    setText("verifier-stdout", fixture.stdout);
    setText("verifier-stderr", fixture.stderr);
    byId("stderr-empty").hidden = fixture.stderr !== "";
    setText("stderr-label", fixture.stderr === "" ? "空字符串" : "标准错误");
    setText("full-contract", JSON.stringify(fixture.contract, null, 2));
    setText("full-trace", fixture.trace_raw);
    setText("copy-status", "");
    setText("load-status", `已加载七条离线记录。当前：${fixture.label}；记录结果：${fixture.contract.decision}。浏览器未执行判定。`);
    byId("fixture-record").hidden = false;
    byId("raw-records").hidden = false;
  }

  function renderBuild(build) {
    document.querySelectorAll("[data-doc]").forEach((link) => {
      const path = link.dataset.doc;
      link.href = `${REPOSITORY}/${path === "traces" ? "tree" : "blob"}/${build.commit}/${path}`;
    });
    setText("build-commit", build.commit);
    byId("build-commit").href = `${REPOSITORY}/commit/${build.commit}`;
    setText("build-dirty", build.dirty ? "dirty = true · 构建时有未提交改动" : "dirty = false · 构建时工作区无未提交改动");
    setText("build-verifier", build.verifier_path);
    byId("build-verifier").href = `${REPOSITORY}/blob/${build.commit}/${build.verifier_path}`;
    setText("build-verifier-hash", build.verifier_sha256);
    setText("build-python", build.python_version);
    setText("build-note", build.dirty
      ? "本地构建包含未提交改动。GitHub 链接固定到记录的提交，但该提交不保证覆盖本地改动；此构建中的源字节身份由记录的 SHA-256 描述，浏览器不进行哈希校验。"
      : "来源与文档链接固定到这次构建的 Git 提交。SHA-256 是构建记录的字节摘要，浏览器只展示该记录，不进行哈希校验。");
    setText("doc-link-note", build.dirty
      ? `文档已固定到构建提交 ${build.commit.slice(0, 12)}；构建时工作区有未提交改动，见上方构建信息。`
      : `文档已固定到构建提交 ${build.commit.slice(0, 12)}。`);
  }

  async function loadFixtures() {
    const retry = byId("retry-load");
    const loadPanel = byId("load-panel");
    retry.disabled = true;
    loadPanel.classList.remove("is-error");
    setText("load-status", "正在读取离线样例记录。这里不会运行工具或重新判定。核心导览和来源文档可继续阅读。");
    const controller = new AbortController();
    const deadline = window.setTimeout(() => controller.abort(), 15000);
    try {
      const response = await fetch("./data/fixtures.json", { signal: controller.signal, cache: "no-store" });
      if (!response.ok) throw new Error(`读取静态数据失败（HTTP ${response.status}）。`);
      let payload;
      try { payload = await response.json(); }
      catch (error) {
        if (error.name === "AbortError") throw error;
        throw new Error("静态数据不是可解析的 JSON。");
      }
      const validated = validateData(payload);
      data = validated;
      const select = byId("fixture-select");
      data.fixtures.forEach((fixture, index) => {
        select.options[index].textContent = `${String(index + 1).padStart(2, "0")} · ${fixture.label}`;
      });
      select.value = data.fixtures[0].id;
      renderBuild(data.build);
      renderFixture(0);
      select.disabled = false;
      retry.hidden = true;
      byId("copy-command").hidden = false;
    } catch (error) {
      data = null;
      byId("fixture-select").disabled = true;
      byId("fixture-record").hidden = true;
      byId("raw-records").hidden = true;
      loadPanel.classList.add("is-error");
      const cause = error.name === "AbortError" ? "读取超过 15 秒。" :
        error instanceof TypeError ? "无法读取静态数据；请检查网络，或通过静态 HTTP 服务打开此页。" : error.message;
      setText("load-status", `未能加载样例记录。${cause}可以重试；核心导览、复现命令和文档链接仍可使用。`);
      retry.hidden = false;
      retry.disabled = false;
    } finally {
      window.clearTimeout(deadline);
    }
  }

  async function copyCommand() {
    const button = byId("copy-command");
    const command = byId("reproduction-command").textContent;
    button.disabled = true;
    try {
      if (!navigator.clipboard || !window.isSecureContext) throw new Error("Clipboard unavailable");
      await navigator.clipboard.writeText(command);
      setText("copy-status", "命令已复制。在本地仓库根目录运行即可；页面没有执行命令。");
    } catch {
      setText("copy-status", "浏览器未允许复制。可在上方命令区选中文字，手动复制。");
    } finally {
      button.disabled = false;
    }
  }

  initializeTour();
  byId("fixture-select").addEventListener("change", (event) => {
    if (!data) return;
    const index = data.fixtures.findIndex((fixture) => fixture.id === event.target.value);
    if (index !== -1) renderFixture(index);
  });
  byId("retry-load").addEventListener("click", loadFixtures);
  byId("copy-command").addEventListener("click", copyCommand);
  loadFixtures();
})();
