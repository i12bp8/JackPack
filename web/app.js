(function () {
  const shared = window.RJShared || {};
  const canvas = document.getElementById("screen");
  const ctx = canvas ? canvas.getContext("2d") : null;
  // Enable high-DPI backing store and high-quality smoothing
  let logicalW = parseInt(canvas ? canvas.getAttribute("width") : 128) || 128,
    logicalH = parseInt(canvas ? canvas.getAttribute("height") : 128) || 128;
  function setupHiDPI() {
    if (!canvas || !ctx) return;
    const DPR = Math.max(1, Math.floor(window.devicePixelRatio || 1));
    canvas.width = logicalW * DPR;
    canvas.height = logicalH * DPR;
    ctx.imageSmoothingEnabled = true;
    try {
      ctx.imageSmoothingQuality = "high";
    } catch {}
  }
  setupHiDPI();
  window.addEventListener("resize", setupHiDPI);
  const statusEl = document.getElementById("status");
  const statusEls = document.querySelectorAll(".status-text");
  const topbarStatus = document.getElementById("topbarStatus");
  const navDevice = document.getElementById("navDevice");
  const navSystem = document.getElementById("navSystem");
  const navNetwork = document.getElementById("navNetwork");
  const navPayloads = document.getElementById("navPayloads");
  const navTerminal = document.getElementById("navTerminal");
  const navLoot = document.getElementById("navLoot");
  const navSettings = document.getElementById("navSettings");
  const sidebar = document.getElementById("sidebar");
  const sidebarBackdrop = document.getElementById("sidebarBackdrop");
  const menuToggle = document.getElementById("menuToggle");
  const deviceTab = document.getElementById("deviceTab");
  const payloadTab = document.getElementById("payloadTab");
  const terminalTab = document.getElementById("terminalTab");
  const networkTab = document.getElementById("networkTab");
  const systemDropdown = document.getElementById("systemDropdown");
  const settingsTab = document.getElementById("settingsTab");
  const lootTab = document.getElementById("lootTab");
  const systemStatus = document.getElementById("systemStatus");
  const sysCpuValue = document.getElementById("sysCpuValue");
  const sysCpuBar = document.getElementById("sysCpuBar");
  const sysTempValue = document.getElementById("sysTempValue");
  const sysMemValue = document.getElementById("sysMemValue");
  const sysMemMeta = document.getElementById("sysMemMeta");
  const sysMemBar = document.getElementById("sysMemBar");
  const sysDiskValue = document.getElementById("sysDiskValue");
  const sysDiskMeta = document.getElementById("sysDiskMeta");
  const sysDiskBar = document.getElementById("sysDiskBar");
  const sysUptime = document.getElementById("sysUptime");
  const sysLoad = document.getElementById("sysLoad");
  const sysPayload = document.getElementById("sysPayload");
  const sysInterfaces = document.getElementById("sysInterfaces");
  const lootList = document.getElementById("lootList");
  const lootPathEl = document.getElementById("lootPath");
  const lootUpBtn = document.getElementById("lootUp");
  const lootStatus = document.getElementById("lootStatus");
  const lootPreview = document.getElementById("lootPreview");
  const lootPreviewTitle = document.getElementById("lootPreviewTitle");
  const lootPreviewBody = document.getElementById("lootPreviewBody");
  const lootPreviewClose = document.getElementById("lootPreviewClose");
  const lootPreviewDownload = document.getElementById("lootPreviewDownload");
  const lootPreviewMeta = document.getElementById("lootPreviewMeta");
  const nmapVizModal = document.getElementById("nmapVizModal");
  const nmapVizTitle = document.getElementById("nmapVizTitle");
  const nmapVizMeta = document.getElementById("nmapVizMeta");
  const nmapVizStatus = document.getElementById("nmapVizStatus");
  const nmapVizBody = document.getElementById("nmapVizBody");
  const nmapVizError = document.getElementById("nmapVizError");
  const nmapVizClose = document.getElementById("nmapVizClose");
  const nmapVizDownloadXml = document.getElementById("nmapVizDownloadXml");
  const nmapVizDownloadJson = document.getElementById("nmapVizDownloadJson");
  const nmapVizFilterVuln = document.getElementById("nmapVizFilterVuln");
  const payloadSidebar = document.getElementById("payloadSidebar");
  const payloadStatus = document.getElementById("payloadStatus");
  const payloadStatusDot = document.getElementById("payloadStatusDot");
  const payloadsRefresh = document.getElementById("payloadsRefresh");
  const payloadsRefreshMain = document.getElementById("payloadsRefreshMain");
  const payloadQuickGrid = document.getElementById("payloadQuickGrid");
  const payloadSearch = document.getElementById("payloadSearch");
  const payloadCategoryList = document.getElementById("payloadCategoryList");
  const payloadCategoryTitle = document.getElementById("payloadCategoryTitle");
  const payloadCategoryDescription = document.getElementById("payloadCategoryDescription");
  const payloadBrowserPanel = document.getElementById("payloadBrowserPanel");
  const payloadDetailPanel = document.getElementById("payloadDetailPanel");
  const payloadDetailTitle = document.getElementById("payloadDetailTitle");
  const payloadDetailPath = document.getElementById("payloadDetailPath");
  const payloadDetailDescription = document.getElementById("payloadDetailDescription");
  const payloadDetailTags = document.getElementById("payloadDetailTags");
  const payloadInlineStatus = document.getElementById("payloadInlineStatus");
  const payloadInlineForm = document.getElementById("payloadInlineForm");
  const payloadInlineRawWrap = document.getElementById("payloadInlineRawWrap");
  const payloadInlineRaw = document.getElementById("payloadInlineRaw");
  const payloadInlineLaunch = document.getElementById("payloadInlineLaunch");
  const payloadLibraryActive = document.getElementById("payloadLibraryActive");
  const payloadLibraryStop = document.getElementById("payloadLibraryStop");
  const payloadLibraryRefresh = document.getElementById("payloadLibraryRefresh");
  const payloadWorkbenchStop = document.getElementById("payloadWorkbenchStop");
  const payloadWorkbenchMeta = document.getElementById("payloadWorkbenchMeta");
  const payloadWorkbenchLogTail = document.getElementById("payloadWorkbenchLogTail");
  const payloadWorkbenchLogStatus = document.getElementById("payloadWorkbenchLogStatus");
  const payloadWorkbenchLogRefresh = document.getElementById("payloadWorkbenchLogRefresh");
  const payloadActionsBlock = document.getElementById("payloadActionsBlock");
  const payloadActionGrid = document.getElementById("payloadActionGrid");
  const payloadControlStatus = document.getElementById("payloadControlStatus");
  const payloadSummary = document.getElementById("payloadSummary");
  const payloadLogTail = document.getElementById("payloadLogTail");
  const payloadLogRefresh = document.getElementById("payloadLogRefresh");
  const payloadLogStatus = document.getElementById("payloadLogStatus");
  const headlessMode = document.getElementById("headlessMode");
  const headlessAp = document.getElementById("headlessAp");
  const headlessAttack = document.getElementById("headlessAttack");
  const activePayloadTitle = document.getElementById("activePayloadTitle");
  const activePayloadMeta = document.getElementById("activePayloadMeta");
  const activePayloadStop = document.getElementById("activePayloadStop");
  const controlApValue = document.getElementById("controlApValue");
  const controlApMeta = document.getElementById("controlApMeta");
  const attackWifiValue = document.getElementById("attackWifiValue");
  const attackWifiMeta = document.getElementById("attackWifiMeta");
  const wiredValue = document.getElementById("wiredValue");
  const wiredMeta = document.getElementById("wiredMeta");
  const homeTempValue = document.getElementById("homeTempValue");
  const homeCpuValue = document.getElementById("homeCpuValue");
  const homeCpuBar = document.getElementById("homeCpuBar");
  const homeMemValue = document.getElementById("homeMemValue");
  const homeMemMeta = document.getElementById("homeMemMeta");
  const homeMemBar = document.getElementById("homeMemBar");
  const homeDiskValue = document.getElementById("homeDiskValue");
  const homeDiskMeta = document.getElementById("homeDiskMeta");
  const homeDiskBar = document.getElementById("homeDiskBar");
  const homeUptimeValue = document.getElementById("homeUptimeValue");
  const homeLoadValue = document.getElementById("homeLoadValue");
  const networkStatus = document.getElementById("networkStatus");
  const networkIface = document.getElementById("networkIface");
  const networkScan = document.getElementById("networkScan");
  const networkRefresh = document.getElementById("networkRefresh");
  const networkDisconnect = document.getElementById("networkDisconnect");
  const networkList = document.getElementById("networkList");
  const networkSelected = document.getElementById("networkSelected");
  const networkPassword = document.getElementById("networkPassword");
  const networkOpen = document.getElementById("networkOpen");
  const networkHidden = document.getElementById("networkHidden");
  const networkForceControl = document.getElementById("networkForceControl");
  const networkConnect = document.getElementById("networkConnect");
  const networkInterfaces = document.getElementById("networkInterfaces");
  const payloadTextModal = document.getElementById("payloadTextModal");
  const payloadTextTitle = document.getElementById("payloadTextTitle");
  const payloadTextMeta = document.getElementById("payloadTextMeta");
  const payloadTextInput = document.getElementById("payloadTextInput");
  const payloadTextSubmit = document.getElementById("payloadTextSubmit");
  const payloadTextCancel = document.getElementById("payloadTextCancel");
  const payloadTextCancelTop = document.getElementById("payloadTextCancelTop");
  const payloadTextBackspace = document.getElementById("payloadTextBackspace");
  const payloadCreatorName = document.getElementById("payloadCreatorName");
  const payloadCreatorIface = document.getElementById("payloadCreatorIface");
  const payloadCreatorDescription = document.getElementById("payloadCreatorDescription");
  const payloadCreatorFields = document.getElementById("payloadCreatorFields");
  const payloadCreatorCreate = document.getElementById("payloadCreatorCreate");
  const payloadCreatorStatus = document.getElementById("payloadCreatorStatus");
  const settingsStatus = document.getElementById("settingsStatus");
  const configStatus = document.getElementById("configStatus");
  const configReload = document.getElementById("configReload");
  const configSave = document.getElementById("configSave");
  const configApIface = document.getElementById("configApIface");
  const configAttackIface = document.getElementById("configAttackIface");
  const configWiredIface = document.getElementById("configWiredIface");
  const configApSsid = document.getElementById("configApSsid");
  const configApPassword = document.getElementById("configApPassword");
  const configHostname = document.getElementById("configHostname");
  const configApAddress = document.getElementById("configApAddress");
  const configApChannel = document.getElementById("configApChannel");
  const configWebPort = document.getElementById("configWebPort");
  const configWsPort = document.getElementById("configWsPort");
  const updateStatus = document.getElementById("updateStatus");
  const updateOutput = document.getElementById("updateOutput");
  const updateNetworkHint = document.getElementById("updateNetworkHint");
  const updateRefreshNetwork = document.getElementById("updateRefreshNetwork");
  const updatePull = document.getElementById("updatePull");
  const updateApply = document.getElementById("updateApply");
  const updateRestart = document.getElementById("updateRestart");
  const diagnosticsStatus = document.getElementById("diagnosticsStatus");
  const diagnosticsRun = document.getElementById("diagnosticsRun");
  const diagnosticsList = document.getElementById("diagnosticsList");
  const diagnosticsSummary = document.getElementById("diagnosticsSummary");
  const discordWebhookInput = document.getElementById("discordWebhookInput");
  const discordWebhookSave = document.getElementById("discordWebhookSave");
  const discordWebhookClear = document.getElementById("discordWebhookClear");
  const wigleApiNameInput = document.getElementById("wigleApiNameInput");
  const wigleApiTokenInput = document.getElementById("wigleApiTokenInput");
  const wigleSave = document.getElementById("wigleSave");
  const wigleClear = document.getElementById("wigleClear");
  const wigleSettingsStatus = document.getElementById("wigleSettingsStatus");
  const tailscaleSettingsStatus = document.getElementById(
    "tailscaleSettingsStatus",
  );
  const tailscaleInstallBtn = document.getElementById("tailscaleInstallBtn");
  const tailscaleReauthBtn = document.getElementById("tailscaleReauthBtn");
  const tailscaleModal = document.getElementById("tailscaleModal");
  const tailscaleKeyInput = document.getElementById("tailscaleKeyInput");
  const tailscaleModalError = document.getElementById("tailscaleModalError");
  const tailscaleModalStatus = document.getElementById("tailscaleModalStatus");
  const tailscaleModalSave = document.getElementById("tailscaleModalSave");
  const tailscaleModalCancel = document.getElementById("tailscaleModalCancel");
  const tailscaleModalClose = document.getElementById("tailscaleModalClose");
  const terminalEl = document.getElementById("terminal");
  const shellStatusEl = document.getElementById("shellStatus");
  const shellConnectBtn = document.getElementById("shellConnect");
  const shellDisconnectBtn = document.getElementById("shellDisconnect");
  const logoutBtn = document.getElementById("logoutBtn");
  const authModal = document.getElementById("authModal");
  const authModalTitle = document.getElementById("authModalTitle");
  const authModalMessage = document.getElementById("authModalMessage");
  const authModalUsername = document.getElementById("authModalUsername");
  const authModalPassword = document.getElementById("authModalPassword");
  const authModalPasswordConfirm = document.getElementById(
    "authModalPasswordConfirm",
  );
  const authModalToken = document.getElementById("authModalToken");
  const authModalRules = document.getElementById("authModalRules");
  const authModalError = document.getElementById("authModalError");
  const authModalToggleRecovery = document.getElementById(
    "authModalToggleRecovery",
  );
  const authModalConfirm = document.getElementById("authModalConfirm");
  const authModalCancel = document.getElementById("authModalCancel");
  const authModalClose = document.getElementById("authModalClose");

  // Build WS URL from current page host.
  function getWsUrl() {
    if (shared.getWsUrl) return shared.getWsUrl(location);
    if (location.protocol === "https:") {
      return `${location.origin.replace(/^https:/, "wss:")}/ws`;
    }
    const p = new URLSearchParams(location.search);
    const host = location.hostname || "raspberrypi.local";
    const port = p.get("port") || "8765";
    return `ws://${host}:${port}/`.replace(/\/\/\//, "//");
  }

  function getApiUrl(path, params = {}) {
    if (shared.getApiUrl) return shared.getApiUrl(path, params, location);
    const qs = new URLSearchParams(params).toString();
    const base = location.origin;
    return `${base}${path}${qs ? `?${qs}` : ""}`;
  }

  function getForwardSearch() {
    try {
      const u = new URL(window.location.href);
      u.searchParams.delete("token");
      const qs = u.searchParams.toString();
      return qs ? `?${qs}` : "";
    } catch {
      return "";
    }
  }

  function escapeHtml(value) {
    return String(value ?? "")
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/\"/g, "&quot;")
      .replace(/'/g, "&#39;");
  }

  function encodeData(value) {
    return encodeURIComponent(String(value ?? ""));
  }

  const AUTH_STORAGE_KEY = "rj.authToken";
  let authToken = "";
  let wsTicket = "";
  let authPromptResolver = null;
  let authInFlight = null;
  let authMode = "login";
  let authRecoveryMode = false;
  let tailscaleReauthMode = false;

  function saveAuthToken(token) {
    if (shared.saveToken) {
      authToken = shared.saveToken(AUTH_STORAGE_KEY, token);
      return;
    }
    authToken = String(token || "").trim();
    try {
      if (authToken) {
        sessionStorage.setItem(AUTH_STORAGE_KEY, authToken);
      } else {
        sessionStorage.removeItem(AUTH_STORAGE_KEY);
      }
    } catch {}
  }

  function loadAuthToken() {
    if (shared.loadToken) {
      const stored = shared.loadToken(AUTH_STORAGE_KEY);
      if (stored) authToken = stored;
    } else {
      try {
        const stored = (sessionStorage.getItem(AUTH_STORAGE_KEY) || "").trim();
        if (stored) authToken = stored;
      } catch {}
    }

    const migrated = shared.migrateTokenFromUrl
      ? shared.migrateTokenFromUrl(AUTH_STORAGE_KEY, "token")
      : "";
    if (migrated) authToken = migrated;
    if (migrated) return;

    // One-time migration: accept token from URL, then remove it.
    try {
      const u = new URL(window.location.href);
      const token = (u.searchParams.get("token") || "").trim();
      if (token) {
        saveAuthToken(token);
        u.searchParams.delete("token");
        window.history.replaceState({}, "", u.toString());
      }
    } catch {}
  }

  function setAuthError(msg) {
    if (!authModalError) return;
    const text = String(msg || "").trim();
    authModalError.textContent = text;
    authModalError.classList.toggle("hidden", !text);
  }

  function setAuthMode(mode, message) {
    authMode = mode;
    if (authModalTitle) {
      authModalTitle.textContent =
        mode === "bootstrap" ? "Create Admin Account" : "Login Required";
    }
    if (authModalMessage) {
      authModalMessage.textContent =
        message ||
        (mode === "bootstrap"
          ? "Set the first admin account for this device."
          : "Log in to continue.");
    }
    const isBootstrap = mode === "bootstrap";
    if (authModalRules) authModalRules.classList.toggle("hidden", !isBootstrap);
    if (authModalPasswordConfirm)
      authModalPasswordConfirm.classList.toggle("hidden", !isBootstrap);
    if (authModalUsername)
      authModalUsername.classList.toggle("hidden", authRecoveryMode);
    if (authModalPassword)
      authModalPassword.classList.toggle("hidden", authRecoveryMode);
    if (authModalToken)
      authModalToken.classList.toggle("hidden", !authRecoveryMode);
    if (authModalToggleRecovery) {
      authModalToggleRecovery.classList.toggle("hidden", isBootstrap);
      authModalToggleRecovery.textContent = authRecoveryMode
        ? "Use username/password login"
        : "Use recovery token instead";
    }
    if (authModalConfirm)
      authModalConfirm.textContent = isBootstrap ? "Create Admin" : "Login";
  }

  function setRecoveryMode(enabled) {
    authRecoveryMode = !!enabled;
    setAuthMode(authMode, authModalMessage ? authModalMessage.textContent : "");
    setAuthError("");
    if (authRecoveryMode) {
      if (authModalToken) authModalToken.focus();
    } else if (authModalUsername) {
      authModalUsername.focus();
    }
  }

  function resolveAuthPrompt(payload) {
    if (!authPromptResolver) return;
    const resolver = authPromptResolver;
    authPromptResolver = null;
    if (authModal) authModal.classList.add("hidden");
    resolver(payload || null);
  }

  function promptForAuth(message, mode = "login") {
    if (
      !authModal ||
      !authModalConfirm ||
      !authModalCancel ||
      !authModalClose
    ) {
      return Promise.resolve(null);
    }
    if (authPromptResolver) {
      return Promise.resolve(null);
    }
    if (authModalUsername) authModalUsername.value = "";
    if (authModalPassword) authModalPassword.value = "";
    if (authModalPasswordConfirm) authModalPasswordConfirm.value = "";
    if (authModalToken) authModalToken.value = authToken || "";
    authRecoveryMode = false;
    setAuthMode(mode, message);
    setAuthError("");
    authModal.classList.remove("hidden");
    setTimeout(() => {
      try {
        if (mode === "bootstrap") {
          authModalUsername && authModalUsername.focus();
        } else if (authModalUsername) {
          authModalUsername.focus();
        }
      } catch {}
    }, 10);
    return new Promise((resolve) => {
      authPromptResolver = resolve;
    });
  }

  function authHeaders(extra) {
    if (shared.authHeaders) return shared.authHeaders(authToken, extra);
    const headers = Object.assign({}, extra || {});
    if (authToken) {
      headers.Authorization = `Bearer ${authToken}`;
    }
    return headers;
  }

  async function apiFetch(url, options = {}, allowRetry = true) {
    const merged = Object.assign({}, options);
    merged.headers = authHeaders(merged.headers);
    merged.credentials = "include";
    const res = await fetch(url, merged);
    if (res.status === 401 && allowRetry) {
      const ok = await ensureAuthenticated("Session expired. Log in again.");
      if (ok) {
        return apiFetch(url, options, false);
      }
    }
    return res;
  }

  async function fetchBootstrapStatus() {
    if (shared.fetchBootstrapStatus) {
      return shared.fetchBootstrapStatus(getApiUrl.bind(null));
    }
    try {
      const res = await fetch(getApiUrl("/api/auth/bootstrap-status"), {
        cache: "no-store",
      });
      const data = await res.json();
      return !!(res.ok && data && data.initialized);
    } catch {
      return true;
    }
  }

  async function fetchAuthMe() {
    if (shared.fetchAuthMe) {
      return shared.fetchAuthMe(getApiUrl.bind(null), authToken);
    }
    try {
      const res = await fetch(getApiUrl("/api/auth/me"), {
        cache: "no-store",
        credentials: "include",
        headers: authHeaders({}),
      });
      if (!res.ok) return null;
      const data = await res.json();
      return data && data.authenticated ? data : null;
    } catch {
      return null;
    }
  }

  async function attemptBootstrap(message) {
    const input = await promptForAuth(
      message || "Set the first admin account for this device.",
      "bootstrap",
    );
    if (!input) return false;
    const username = String(input.username || "").trim();
    const password = String(input.password || "");
    const confirm = String(input.confirm || "");
    if (!username || !password) {
      setAuthError("Username and password are required.");
      return attemptBootstrap(message);
    }
    if (username.length < 3) {
      setAuthError("username must be at least 3 characters");
      return attemptBootstrap(message);
    }
    if (username.length > 32) {
      setAuthError("username too long");
      return attemptBootstrap(message);
    }
    if (password.length < 8) {
      setAuthError("password must be at least 8 characters");
      return attemptBootstrap(message);
    }
    if (password !== confirm) {
      setAuthError("Passwords do not match.");
      return attemptBootstrap(message);
    }
    try {
      const res = await fetch(getApiUrl("/api/auth/bootstrap"), {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        credentials: "include",
        body: JSON.stringify({ username, password }),
      });
      const data = await res.json();
      if (!res.ok) {
        if (res.status === 409) {
          return attemptLogin("Admin already exists. Log in to continue.");
        }
        setAuthError(data && data.error ? data.error : "Bootstrap failed");
        return attemptBootstrap(message);
      }
      saveAuthToken("");
      return true;
    } catch {
      setAuthError("Bootstrap request failed.");
      return attemptBootstrap(message);
    }
  }

  async function attemptLogin(message) {
    const input = await promptForAuth(
      message || "Log in to continue.",
      "login",
    );
    if (!input) return false;

    if (input.recovery) {
      const token = String(input.token || "").trim();
      if (!token) {
        setAuthError("Recovery token is required.");
        return attemptLogin(message);
      }
      saveAuthToken(token);
      try {
        const meRes = await fetch(getApiUrl("/api/auth/me"), {
          cache: "no-store",
          headers: authHeaders({}),
          credentials: "include",
        });
        if (!meRes.ok) {
          setAuthError("Invalid recovery token.");
          return attemptLogin(message);
        }
        return true;
      } catch {
        setAuthError("Recovery auth failed.");
        return attemptLogin(message);
      }
    }

    const username = String(input.username || "").trim();
    const password = String(input.password || "");
    if (!username || !password) {
      setAuthError("Username and password are required.");
      return attemptLogin(message);
    }
    try {
      const res = await fetch(getApiUrl("/api/auth/login"), {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        credentials: "include",
        body: JSON.stringify({ username, password }),
      });
      const data = await res.json();
      if (!res.ok) {
        setAuthError(data && data.error ? data.error : "Login failed");
        return attemptLogin(message);
      }
      saveAuthToken("");
      return true;
    } catch {
      setAuthError("Login request failed.");
      return attemptLogin(message);
    }
  }

  async function refreshWsTicket() {
    wsTicket = "";
    if (shared.refreshWsTicket) {
      wsTicket = await shared.refreshWsTicket(getApiUrl.bind(null), authToken);
      return;
    }
    if (authToken) return;
    try {
      const res = await fetch(getApiUrl("/api/auth/ws-ticket"), {
        method: "POST",
        credentials: "include",
      });
      const data = await res.json();
      if (res.ok && data && data.ticket) {
        wsTicket = String(data.ticket);
      }
    } catch {}
  }

  async function ensureAuthenticated(message) {
    if (authInFlight) {
      return authInFlight;
    }
    authInFlight = (async () => {
      const me = await fetchAuthMe();
      if (me) {
        await refreshWsTicket();
        return true;
      }

      const initialized = await fetchBootstrapStatus();
      if (!initialized) {
        const bootOk = await attemptBootstrap(message);
        if (!bootOk) return false;
        await refreshWsTicket();
        return true;
      }
      const loginOk = await attemptLogin(message);
      if (!loginOk) return false;
      await refreshWsTicket();
      return true;
    })();
    try {
      return await authInFlight;
    } finally {
      authInFlight = null;
    }
  }

  async function logoutUser() {
    try {
      await fetch(getApiUrl("/api/auth/logout"), {
        method: "POST",
        credentials: "include",
      });
    } catch {}
    saveAuthToken("");
    wsTicket = "";
    try {
      if (ws) ws.close();
    } catch {}
    window.location.reload();
  }

  let ws = null;
  let reconnectTimer = null;
  const pressed = new Set(); // keyboard pressed state
  let activeTab = "device";
  let lootState = { path: "", parent: "" };
  let nmapVizState = { data: null, jsonUrl: "" };
  let payloadState = {
    categories: [],
    open: {},
    activePath: null,
    activeSchema: null,
    selectedPath: "",
    selectedSchema: null,
    workflow: { path: "", networks: [], selectedBssids: {}, portals: [], status: "" },
    selectedCategory: "",
    query: "",
    schemaCache: {},
  };
  let networkState = { interfaces: [], selectedNetwork: null };
  let networkStatusLoadedAt = 0;
  let networkStatusPromise = null;
  let textSessionState = { active: false, sessionId: "", defaultValue: "" };
  let term = null;
  let fitAddon = null;
  let shellOpen = false;
  let terminalHasFocus = false;
  let shellWanted = false;
  let pendingShellCommands = [];
  let systemOpen = false;
  let wsAuthenticated = true;

  function applyStatusTone(el, txt) {
    if (!el) return;
    const s = String(txt || "").toLowerCase();
    el.classList.remove(
      "status-tone-ok",
      "status-tone-warn",
      "status-tone-bad",
    );
    if (
      /connected|authenticated|ready|live|saved|configured|launched|running/.test(
        s,
      )
    ) {
      el.classList.add("status-tone-ok");
    } else if (/loading|connecting|opening|reconnecting|stopping/.test(s)) {
      el.classList.add("status-tone-warn");
    } else if (/failed|unavailable|disconnected|error|denied/.test(s)) {
      el.classList.add("status-tone-bad");
    }
  }

  function setStatus(txt) {
    if (topbarStatus) {
      topbarStatus.textContent = txt;
      applyStatusTone(topbarStatus, txt);
    }
    if (statusEl) {
      statusEl.textContent = txt;
      applyStatusTone(statusEl, txt);
    }
    if (statusEls && statusEls.length) {
      statusEls.forEach((el) => {
        el.textContent = txt;
        applyStatusTone(el, txt);
      });
    }
  }

  function setPayloadStatus(txt) {
    if (payloadStatus) {
      payloadStatus.textContent = txt;
      applyStatusTone(payloadStatus, txt);
    }
    if (payloadStatusDot) {
      const active = /running|starting|stopping|launched/i.test(
        String(txt || ""),
      );
      payloadStatusDot.classList.toggle("running", active);
    }
  }

  function setPayloadLogStatus(txt) {
    if (payloadLogStatus) {
      payloadLogStatus.textContent = txt;
      applyStatusTone(payloadLogStatus, txt);
    }
    if (payloadWorkbenchLogStatus) {
      payloadWorkbenchLogStatus.textContent = txt;
      applyStatusTone(payloadWorkbenchLogStatus, txt);
    }
  }

  function setPayloadCreatorStatus(txt) {
    if (!payloadCreatorStatus) return;
    payloadCreatorStatus.textContent = txt;
    applyStatusTone(payloadCreatorStatus, txt);
  }

  function payloadLabel(path) {
    const raw = String(path || "");
    const base = raw.split("/").pop() || raw || "payload";
    return base.replace(/\.py$/i, "").replace(/_/g, " ");
  }

  function setActivePayloadView(status) {
    const running = !!(status && status.running);
    const path = running ? status.path || "" : "";
    if (activePayloadTitle) {
      activePayloadTitle.textContent = running ? payloadLabel(path) : "None";
    }
    if (payloadLibraryActive) {
      payloadLibraryActive.textContent = running ? payloadLabel(path) : "None";
    }
    if (activePayloadMeta) {
      if (!running) {
        activePayloadMeta.textContent = "Ready";
      } else if (status.started_at) {
        activePayloadMeta.textContent = `${path} · ${formatDuration(Date.now() / 1000 - Number(status.started_at || 0))}`;
      } else {
        activePayloadMeta.textContent = path || "running";
      }
    }
    if (payloadWorkbenchMeta) {
      if (!running) {
        payloadWorkbenchMeta.textContent = "Ready";
      } else if (status.started_at) {
        payloadWorkbenchMeta.textContent = `${path} · ${formatDuration(Date.now() / 1000 - Number(status.started_at || 0))}`;
      } else {
        payloadWorkbenchMeta.textContent = path || "running";
      }
    }
    if (activePayloadStop) {
      activePayloadStop.classList.toggle("hidden", !running);
    }
    if (payloadLibraryStop) {
      payloadLibraryStop.classList.toggle("hidden", !running);
    }
    if (payloadWorkbenchStop) {
      payloadWorkbenchStop.classList.toggle("hidden", !running);
    }
    renderPayloadActions();
  }

  function actionIcon(button) {
    const icons = {
      UP: "fa-arrow-up",
      DOWN: "fa-arrow-down",
      LEFT: "fa-arrow-left",
      RIGHT: "fa-arrow-right",
      OK: "fa-check",
      KEY1: "fa-bolt",
      KEY2: "fa-sliders",
      KEY3: "fa-arrow-left-long",
    };
    return icons[button] || "fa-circle-dot";
  }

  function renderPayloadActions() {
    if (!payloadActionGrid) return;
    const running = !!payloadState.activePath;
    const schema = payloadState.activeSchema || {};
    const legacyButtons = new Set(["UP", "DOWN", "LEFT", "RIGHT", "OK", "KEY1", "KEY2", "KEY3"]);
    const actions = (Array.isArray(schema.actions) ? schema.actions : []).filter((action) => {
      const button = String(action.button || "").toUpperCase();
      return !legacyButtons.has(button) || action.web_native === true || action.headless === true;
    });
    if (payloadControlStatus) {
      payloadControlStatus.textContent = running
        ? `Runtime controls for ${payloadLabel(payloadState.activePath)}`
        : payloadState.selectedPath
          ? `${payloadLabel(payloadState.selectedPath)} selected.`
          : "Choose a payload.";
    }
    if (payloadActionsBlock) {
      payloadActionsBlock.classList.toggle("hidden", !actions.length);
    }
    if (!actions.length) {
      payloadActionGrid.innerHTML = "";
      return;
    }
    payloadActionGrid.innerHTML = actions
      .map((action) => {
        const button = String(action.button || "").toUpperCase();
        const label = escapeHtml(action.label || button);
        const desc = escapeHtml(action.description || "");
        return `<button type="button" data-payload-action="${escapeHtml(button)}" ${running ? "" : "disabled"} class="jp-action-btn ${running ? "" : "opacity-45 cursor-not-allowed"}">
          <i class="fa-solid ${actionIcon(button)}"></i>
          <span>
            <strong>${label}</strong>
            ${desc ? `<small>${desc}</small>` : ""}
          </span>
        </button>`;
      })
      .join("");
  }

  function setSystemStatus(txt) {
    if (systemStatus) {
      systemStatus.textContent = txt;
      applyStatusTone(systemStatus, txt);
    }
  }

  function setShellStatus(txt) {
    if (shellStatusEl) {
      shellStatusEl.textContent = txt;
      applyStatusTone(shellStatusEl, txt);
    }
  }

  function setSettingsStatus(txt) {
    if (settingsStatus) {
      settingsStatus.textContent = txt;
      applyStatusTone(settingsStatus, txt);
    }
  }

  function setNetworkStatus(txt) {
    if (networkStatus) {
      networkStatus.textContent = txt;
      applyStatusTone(networkStatus, txt);
    }
  }

  function setConfigStatus(txt) {
    if (configStatus) {
      configStatus.textContent = txt;
      applyStatusTone(configStatus, txt);
    }
  }

  function setUpdateStatus(txt) {
    if (updateStatus) {
      updateStatus.textContent = txt;
      applyStatusTone(updateStatus, txt);
    }
  }

  function setDiagnosticsStatus(txt) {
    if (diagnosticsStatus) {
      diagnosticsStatus.textContent = txt;
      applyStatusTone(diagnosticsStatus, txt);
    }
  }

  function setTailscaleStatus(txt) {
    if (tailscaleSettingsStatus) {
      tailscaleSettingsStatus.textContent = txt;
      applyStatusTone(tailscaleSettingsStatus, txt);
    }
  }

  function setWigleStatus(txt) {
    if (wigleSettingsStatus) {
      wigleSettingsStatus.textContent = txt;
      applyStatusTone(wigleSettingsStatus, txt);
    }
  }

  function getWigleConfiguredStatus(data) {
    if (!data || !data.configured) return "WiGLE not configured";
    const parts = [];
    if (data.api_name_masked) parts.push(`Name ${data.api_name_masked}`);
    if (data.api_token_masked) parts.push(`Token ${data.api_token_masked}`);
    return parts.length
      ? `WiGLE configured: ${parts.join(" | ")}`
      : "WiGLE configured";
  }

  function applyWigleSettingsToUI(data) {
    const configured = !!(data && data.configured);
    const nameMasked = String((data && data.api_name_masked) || "");
    const tokenMasked = String((data && data.api_token_masked) || "");
    if (wigleApiNameInput) {
      wigleApiNameInput.value = "";
      wigleApiNameInput.placeholder =
        configured && nameMasked ? `Saved: ${nameMasked}` : "WiGLE API name";
    }
    if (wigleApiTokenInput) {
      wigleApiTokenInput.value = "";
      wigleApiTokenInput.placeholder =
        configured && tokenMasked ? `Saved: ${tokenMasked}` : "WiGLE API token";
    }
  }

  function setSidebarOpen(open) {
    if (!sidebar) return;
    sidebar.classList.toggle("-translate-x-full", !open);
    sidebar.classList.toggle("translate-x-0", open);
    if (sidebarBackdrop) {
      sidebarBackdrop.classList.toggle("hidden", !open);
    }
  }

  function setNavActive(btn, active) {
    if (!btn) return;
    btn.classList.toggle("nav-active", active);
  }

  function setActiveTab(tab) {
    activeTab = tab;
    const isDevice = tab === "device";
    if (deviceTab) deviceTab.classList.toggle("hidden", !isDevice);
    if (payloadTab) payloadTab.classList.toggle("hidden", tab !== "payloads");
    if (terminalTab) terminalTab.classList.toggle("hidden", tab !== "terminal");
    if (networkTab) networkTab.classList.toggle("hidden", tab !== "network");
    if (settingsTab) settingsTab.classList.toggle("hidden", tab !== "settings");
    if (lootTab) lootTab.classList.toggle("hidden", tab !== "loot");
    setNavActive(navDevice, isDevice);
    setNavActive(navNetwork, tab === "network");
    setNavActive(navPayloads, tab === "payloads");
    setNavActive(navTerminal, tab === "terminal");
    setNavActive(navLoot, tab === "loot");
    setNavActive(navSettings, tab === "settings");
    document.querySelectorAll("[data-mobile-tab]").forEach((btn) => {
      const active = btn.getAttribute("data-mobile-tab") === tab;
      btn.classList.toggle("jp-mobile-active", active);
    });
    if (tab === "terminal") {
      ensureTerminal();
      window.requestAnimationFrame(() => {
        sendShellResize();
        try {
          term && term.focus();
        } catch {}
      });
    }
    setSidebarOpen(false);
  }

  function setSystemOpen(open) {
    systemOpen = !!open;
    if (systemDropdown) {
      systemDropdown.classList.toggle("hidden", !systemOpen);
    }
    setNavActive(navSystem, systemOpen);
    if (systemOpen) {
      loadSystemStatus();
    }
  }

  function connect() {
    if (
      ws &&
      (ws.readyState === WebSocket.OPEN ||
        ws.readyState === WebSocket.CONNECTING)
    )
      return;
    const url = getWsUrl();
    try {
      ws = new WebSocket(url);
    } catch (e) {
      setStatus("WebSocket failed to construct");
      scheduleReconnect();
      return;
    }

    ws.onopen = () => {
      setStatus("Connected");
      wsAuthenticated = true;
      if (wsTicket) {
        try {
          ws.send(JSON.stringify({ type: "auth_session", ticket: wsTicket }));
        } catch {}
      } else if (authToken) {
        try {
          ws.send(JSON.stringify({ type: "auth", token: authToken }));
        } catch {}
      }
      if (shellWanted) {
        sendShellOpen();
      }
    };

    ws.onmessage = (ev) => {
      try {
        const msg = JSON.parse(ev.data);
        if (msg.type === "frame" && msg.data) {
          if (!canvas || !ctx) return;
          const img = new Image();
          img.onload = () => {
            try {
              if (
                img.naturalWidth !== logicalW ||
                img.naturalHeight !== logicalH
              ) {
                logicalW = img.naturalWidth;
                logicalH = img.naturalHeight;
                setupHiDPI();
                [canvas].forEach((c) => {
                  if (!c) return;
                  c.style.aspectRatio = logicalW + "/" + logicalH;
                  c.classList.remove("aspect-square");
                });
              }
              ctx.clearRect(0, 0, canvas.width, canvas.height);
              ctx.drawImage(img, 0, 0, canvas.width, canvas.height);
            } catch {}
          };
          img.src = "data:image/jpeg;base64," + msg.data;
          return;
        }
        if (msg.type === "auth_required") {
          wsAuthenticated = false;
          if (wsTicket) {
            try {
              ws.send(
                JSON.stringify({ type: "auth_session", ticket: wsTicket }),
              );
            } catch {}
            return;
          }
          if (authToken) {
            try {
              ws.send(JSON.stringify({ type: "auth", token: authToken }));
            } catch {}
            return;
          }
          ensureAuthenticated("Authentication required to use WebSocket.").then(
            () => {
              if (!ws || ws.readyState !== WebSocket.OPEN) return;
              if (wsTicket) {
                try {
                  ws.send(
                    JSON.stringify({ type: "auth_session", ticket: wsTicket }),
                  );
                } catch {}
              } else if (authToken) {
                try {
                  ws.send(JSON.stringify({ type: "auth", token: authToken }));
                } catch {}
              }
            },
          );
          return;
        }
        if (msg.type === "auth_ok") {
          wsAuthenticated = true;
          setStatus("Authenticated");
          if (shellWanted) sendShellOpen();
          return;
        }
        if (msg.type === "auth_error") {
          wsAuthenticated = false;
          setStatus("Auth failed");
          return;
        }
        if (msg.type === "shell_ready") {
          shellOpen = true;
          terminalEl?.closest(".terminal-wrap")?.classList.add("shell-open");
          setShellStatus("Connected");
          sendShellResize();
          flushPendingShellCommands();
          return;
        }
        if (msg.type === "shell_out" && msg.data) {
          ensureTerminal();
          if (term) term.write(msg.data);
          return;
        }
        if (msg.type === "shell_exit") {
          shellOpen = false;
          terminalEl?.closest(".terminal-wrap")?.classList.remove("shell-open");
          setShellStatus("Exited");
        }
        if (msg.type === "text_session") {
          handleTextSession(msg);
          return;
        }
      } catch {}
    };

    ws.onclose = () => {
      setStatus("Disconnected – reconnecting…");
      setShellStatus("Disconnected");
      shellOpen = false;
      terminalEl?.closest(".terminal-wrap")?.classList.remove("shell-open");
      scheduleReconnect();
    };

    ws.onerror = () => {
      try {
        ws.close();
      } catch {}
    };
  }

  function scheduleReconnect() {
    if (reconnectTimer) return;
    reconnectTimer = setTimeout(() => {
      reconnectTimer = null;
      connect();
    }, 1000);
  }

  function ensureTerminal() {
    if (!terminalEl) return null;
    if (!window.Terminal) {
      setShellStatus("xterm missing");
      return null;
    }
    if (!term) {
      term = new window.Terminal({
        cursorBlink: true,
        fontSize: 14,
        scrollback: 5000,
        convertEol: true,
        fastScrollModifier: "alt",
        theme: {
          background: "#01030a",
          foreground: "#f7f8ff",
          cursor: "#58ffb0",
          selectionBackground: "#b36bff66",
        },
      });
      if (window.FitAddon && window.FitAddon.FitAddon) {
        fitAddon = new window.FitAddon.FitAddon();
        term.loadAddon(fitAddon);
      }
      term.open(terminalEl);
      term.onData((data) => sendShellInput(data));
      if (terminalEl) {
        terminalEl.addEventListener("focusin", () => {
          terminalHasFocus = true;
        });
        terminalEl.addEventListener("focusout", () => {
          terminalHasFocus = false;
        });
        terminalEl.addEventListener("mousedown", () => {
          try {
            term.focus();
          } catch {}
        });
      }
      if (fitAddon) {
        try {
          fitAddon.fit();
        } catch {}
      }
      term.write("JackPack shell ready.\\r\\n");
    }
    return term;
  }

  function sendShellInput(data) {
    if (!ws || ws.readyState !== WebSocket.OPEN) return;
    if (!shellOpen) return;
    try {
      ws.send(JSON.stringify({ type: "shell_in", data }));
    } catch {}
  }

  function flushPendingShellCommands() {
    if (!pendingShellCommands.length) return;
    const queued = pendingShellCommands.splice(0);
    setTimeout(() => {
      queued.forEach((command) => sendShellInput(`${command}\n`));
    }, 80);
  }

  function sendShellCommand(command) {
    const clean = String(command || "").trim();
    if (!clean) return;
    if (!shellOpen) {
      pendingShellCommands.push(clean);
      sendShellOpen();
      return;
    }
    sendShellInput(`${clean}\n`);
  }

  function sendShellOpen() {
    shellWanted = true;
    if (!ws || ws.readyState !== WebSocket.OPEN) return;
    ensureTerminal();
    terminalEl?.closest(".terminal-wrap")?.classList.add("shell-open");
    setShellStatus("Opening...");
    try {
      ws.send(JSON.stringify({ type: "shell_open" }));
    } catch {}
  }

  function sendShellClose() {
    shellWanted = false;
    if (ws && ws.readyState === WebSocket.OPEN) {
      try {
        ws.send(JSON.stringify({ type: "shell_close" }));
      } catch {}
    }
    shellOpen = false;
    terminalEl?.closest(".terminal-wrap")?.classList.remove("shell-open");
    setShellStatus("Closed");
  }

  function sendShellResize() {
    if (!ws || ws.readyState !== WebSocket.OPEN) return;
    if (!shellOpen || !term) return;
    if (fitAddon) {
      try {
        fitAddon.fit();
      } catch {}
    }
    try {
      ws.send(
        JSON.stringify({
          type: "shell_resize",
          cols: term.cols,
          rows: term.rows,
        }),
      );
    } catch {}
  }

  function formatBytes(bytes) {
    if (bytes === 0) return "0 B";
    const k = 1024;
    const sizes = ["B", "KB", "MB", "GB"];
    const i = Math.min(
      sizes.length - 1,
      Math.floor(Math.log(bytes) / Math.log(k)),
    );
    const value = bytes / Math.pow(k, i);
    return `${value.toFixed(value >= 10 || i === 0 ? 0 : 1)} ${sizes[i]}`;
  }

  function formatDuration(totalSec) {
    const s = Math.max(0, Number(totalSec || 0) | 0);
    const d = Math.floor(s / 86400);
    const h = Math.floor((s % 86400) / 3600);
    const m = Math.floor((s % 3600) / 60);
    if (d > 0) return `${d}d ${h}h ${m}m`;
    if (h > 0) return `${h}h ${m}m`;
    return `${m}m`;
  }

  function pct(used, total) {
    if (!total || total <= 0) return 0;
    return Math.max(0, Math.min(100, (used / total) * 100));
  }

  function bar(el, value) {
    if (!el) return;
    el.style.width = `${Math.max(0, Math.min(100, value)).toFixed(1)}%`;
  }

  async function loadSystemStatus() {
    setSystemStatus("Loading...");
    try {
      const url = getApiUrl("/api/system/status");
      const res = await apiFetch(url, { cache: "no-store" });
      const data = await res.json();
      if (!res.ok) {
        throw new Error(data && data.error ? data.error : "system_failed");
      }

      const cpu = Number(data.cpu_percent ?? data.cpu ?? 0);
      const memUsed = Number(data.mem_used ?? data.memory_used ?? data.memory?.used ?? 0);
      const memTotal = Number(data.mem_total ?? data.memory_total ?? data.memory?.total ?? 0);
      const diskUsed = Number(data.disk_used ?? data.disk?.used ?? 0);
      const diskTotal = Number(data.disk_total ?? data.disk?.total ?? 0);
      const memPct = pct(memUsed, memTotal);
      const diskPct = pct(diskUsed, diskTotal);

      if (sysCpuValue) sysCpuValue.textContent = `${cpu.toFixed(1)}%`;
      if (homeCpuValue) homeCpuValue.textContent = `${cpu.toFixed(1)}%`;
      if (sysTempValue) {
        if (data.temp_c === null || data.temp_c === undefined) {
          sysTempValue.textContent = "--.- C";
        } else {
          sysTempValue.textContent = `${Number(data.temp_c).toFixed(1)} C`;
        }
      }
      if (homeTempValue) {
        homeTempValue.textContent =
          data.temp_c === null || data.temp_c === undefined
            ? "--.- C"
            : `${Number(data.temp_c).toFixed(1)} C`;
      }
      bar(sysCpuBar, cpu);
      bar(homeCpuBar, cpu);

      if (sysMemValue) sysMemValue.textContent = `${memPct.toFixed(1)}%`;
      if (sysMemMeta)
        sysMemMeta.textContent = `${formatBytes(memUsed)} / ${formatBytes(memTotal)}`;
      bar(sysMemBar, memPct);
      if (homeMemValue) homeMemValue.textContent = `${memPct.toFixed(1)}%`;
      if (homeMemMeta)
        homeMemMeta.textContent = `${formatBytes(memUsed)} / ${formatBytes(memTotal)}`;
      bar(homeMemBar, memPct);

      if (sysDiskValue) sysDiskValue.textContent = `${diskPct.toFixed(1)}%`;
      if (sysDiskMeta)
        sysDiskMeta.textContent = `${formatBytes(diskUsed)} / ${formatBytes(diskTotal)}`;
      bar(sysDiskBar, diskPct);
      if (homeDiskValue) homeDiskValue.textContent = `${diskPct.toFixed(1)}%`;
      if (homeDiskMeta)
        homeDiskMeta.textContent = `${formatBytes(diskUsed)} / ${formatBytes(diskTotal)}`;
      bar(homeDiskBar, diskPct);

      if (sysUptime) sysUptime.textContent = formatDuration(data.uptime_s);
      if (homeUptimeValue) homeUptimeValue.textContent = formatDuration(data.uptime_s);
      if (sysLoad)
        sysLoad.textContent = Array.isArray(data.load)
          ? data.load.join(", ")
          : "-";
      if (homeLoadValue)
        homeLoadValue.textContent = Array.isArray(data.load)
          ? `Load ${data.load.join(", ")}`
          : "Load -";
      if (sysPayload)
        sysPayload.textContent = data.payload_running
          ? data.payload_path || "running"
          : "none";

      if (sysInterfaces) {
        const ifaces = Array.isArray(data.interfaces) ? data.interfaces : [];
        if (!ifaces.length) {
          sysInterfaces.innerHTML =
            '<div class="text-slate-500">No active interfaces</div>';
        } else {
          sysInterfaces.innerHTML = ifaces
            .map(
              (i) =>
                `<div><span class="text-emerald-300">${escapeHtml(String(i.name || "-"))}</span>: ${escapeHtml(String(i.ipv4 || "-"))} <span class="text-slate-500">${escapeHtml(String(i.role || "network"))}</span></div>`,
            )
            .join("");
        }
      }

      setSystemStatus("Live");
    } catch (e) {
      setSystemStatus("Unavailable");
      if (homeCpuValue) homeCpuValue.textContent = "--";
      if (homeTempValue) homeTempValue.textContent = "--.- C";
      if (homeMemValue) homeMemValue.textContent = "--";
      if (homeMemMeta) homeMemMeta.textContent = "Unavailable";
      if (homeDiskValue) homeDiskValue.textContent = "--";
      if (homeDiskMeta) homeDiskMeta.textContent = "Unavailable";
      if (homeUptimeValue) homeUptimeValue.textContent = "--";
      if (homeLoadValue) homeLoadValue.textContent = "Load --";
    }
  }

  function ifaceByRole(ifaces, role, fallbackName) {
    return (
      (ifaces || []).find((item) => item.role === role) ||
      (ifaces || []).find((item) => item.name === fallbackName) ||
      null
    );
  }

  async function loadHeadlessStatus() {
    try {
      const url = getApiUrl("/api/headless/status");
      const res = await apiFetch(url, { cache: "no-store" });
      const data = await res.json();
      if (!res.ok) throw new Error(data && data.error ? data.error : "headless_failed");
      const ifaces = Array.isArray(data.interfaces) ? data.interfaces : [];
      const ap = data.ap || {};
      const attack = data.attack || {};
      const wired = ifaceByRole(ifaces, "wired_target", (data.wired && data.wired.iface) || "eth0");

      if (headlessMode) {
        headlessMode.textContent = data.headless ? "Headless" : "Classic";
      }
      if (headlessAp) {
        headlessAp.textContent = `${ap.ssid || "JackPack"} · ${ap.iface || "wlan0"}${ap.present ? "" : " missing"}`;
      }
      if (headlessAttack) {
        headlessAttack.textContent = `${attack.iface || "wlan1"} ${attack.present ? "ready" : "missing"}`;
      }
      if (controlApValue) controlApValue.textContent = `${ap.iface || "wlan0"} · ${ap.ssid || "JackPack"}`;
      if (controlApMeta) {
        const web = data.web || {};
        controlApMeta.textContent = ap.present ? (web.url || "http://jackpack.local:8080") : "Missing";
      }
      if (attackWifiValue) attackWifiValue.textContent = attack.iface || "wlan1";
      if (attackWifiMeta) attackWifiMeta.textContent = attack.present ? "Detected" : "Plug in USB adapter";
      if (wiredValue) wiredValue.textContent = wired ? `${wired.name} · ${wired.ipv4 || "-"}` : ((data.wired && data.wired.iface) || "eth0");
      if (wiredMeta) wiredMeta.textContent = wired ? "Online" : "No address";
      if (data.payload) setActivePayloadView(data.payload);
    } catch (e) {
      if (headlessMode) headlessMode.textContent = "Status unavailable";
    }
  }

  function ifaceLabel(item) {
    const role = String(item?.role || "network").replace("_", " ");
    const bits = [item?.name || "iface", role];
    if (item?.recommended) bits.push("recommended");
    if (item?.protected) bits.push("control AP");
    return bits.join(" · ");
  }

  function renderNetworkInterfaces() {
    if (networkInterfaces) {
      const items = networkState.interfaces || [];
      networkInterfaces.innerHTML = items.length
        ? items
            .map((item) => {
              const tone = item.protected
                ? "text-amber-300"
                : item.recommended
                  ? "text-emerald-300"
                  : "text-slate-300";
              const ip = item.ipv4 || "-";
              const state = item.state || "unknown";
              const connection = item.connection ? ` · ${escapeHtml(item.connection)}` : "";
              return `<div class="jp-iface-row">
                <div>
                  <div class="font-semibold ${tone}">${escapeHtml(item.name || "-")}</div>
                  <div class="text-[11px] text-slate-500">${escapeHtml(String(item.role || "network").replace("_", " "))}${connection}</div>
                </div>
                <div class="text-right">
                  <div class="text-xs text-slate-200">${escapeHtml(state)}</div>
                  <div class="text-[11px] text-slate-500">${escapeHtml(ip)}</div>
                </div>
              </div>`;
            })
            .join("")
        : '<div class="text-xs text-slate-500">No interfaces detected yet.</div>';
    }
    if (!networkIface) return;
    const previous = networkIface.value;
    const wifiItems = (networkState.interfaces || []).filter((item) => item.wireless || item.role === "control_ap" || item.role === "attack_wifi");
    networkIface.innerHTML = wifiItems
      .map((item) => `<option value="${escapeHtml(item.name)}">${escapeHtml(ifaceLabel(item))}</option>`)
      .join("");
    const preferred =
      wifiItems.find((item) => item.recommended && item.present) ||
      wifiItems.find((item) => item.role === "attack_wifi") ||
      wifiItems[0];
    if (previous && wifiItems.some((item) => item.name === previous)) {
      networkIface.value = previous;
    } else if (preferred) {
      networkIface.value = preferred.name;
    }
  }

  function renderNetworkList(items) {
    if (!networkList) return;
    if (!items || !items.length) {
      networkList.innerHTML = '<div class="text-xs text-slate-500 p-3">No networks loaded. Pick an interface and scan.</div>';
      return;
    }
    networkList.innerHTML = items
      .map((net, idx) => {
        const ssid = net.ssid || "(hidden)";
        const security = net.open ? "Open" : net.security || "Secured";
        const signal = net.signal === null || net.signal === undefined ? "-" : `${net.signal}%`;
        const selected = networkState.selectedNetwork && networkState.selectedNetwork.bssid === net.bssid;
        return `<button type="button" data-network-index="${idx}" class="jp-network-row ${selected ? "jp-network-selected" : ""}">
          <div class="min-w-0">
            <div class="jp-network-ssid">${escapeHtml(ssid)}</div>
            <div class="jp-network-meta">${escapeHtml(security)} · ch ${escapeHtml(net.channel || "-")} · ${escapeHtml(net.bssid || "")}</div>
          </div>
          <div class="jp-network-signal">${escapeHtml(signal)}</div>
        </button>`;
      })
      .join("");
    networkList.dataset.networks = JSON.stringify(items);
  }

  function selectNetwork(net) {
    networkState.selectedNetwork = net || null;
    if (networkSelected) {
      networkSelected.textContent = net ? (net.ssid || "(hidden)") : "Select a network";
    }
    if (networkOpen) {
      networkOpen.checked = !!(net && net.open);
    }
    if (networkPassword) {
      networkPassword.disabled = !!(net && net.open);
      networkPassword.placeholder = net && net.open ? "Open network" : "Network password";
      if (net && net.open) networkPassword.value = "";
    }
    try {
      const items = JSON.parse(networkList?.dataset.networks || "[]");
      renderNetworkList(items);
    } catch {}
  }

  async function loadNetworkStatus(options = {}) {
    const force = !!options.force;
    const silent = !!options.silent;
    const fresh = Date.now() - networkStatusLoadedAt < 15000;
    if (!force && fresh && networkState.interfaces.length) {
      renderNetworkInterfaces();
      return networkState.interfaces;
    }
    if (networkStatusPromise) return networkStatusPromise;
    if (!silent) setNetworkStatus("Loading...");
    networkStatusPromise = (async () => {
      try {
        const res = await apiFetch(getApiUrl("/api/network/status"), { cache: "no-store" });
        const data = await res.json();
        if (!res.ok || !data.ok) throw new Error(data && data.error ? data.error : "network_failed");
        networkState.interfaces = Array.isArray(data.interfaces) ? data.interfaces : [];
        networkStatusLoadedAt = Date.now();
        renderNetworkInterfaces();
        if (!silent) setNetworkStatus(data.nmcli ? "Ready" : "nmcli missing");
        return networkState.interfaces;
      } catch (e) {
        if (!silent) setNetworkStatus("Unavailable");
        return networkState.interfaces;
      } finally {
        networkStatusPromise = null;
      }
    })();
    return networkStatusPromise;
  }

  async function scanNetworks() {
    const iface = networkIface ? networkIface.value : "";
    if (!iface) {
      setNetworkStatus("Pick an interface");
      return;
    }
    selectNetwork(null);
    setNetworkStatus(`Scanning ${iface}...`);
    try {
      const res = await apiFetch(getApiUrl("/api/network/scan"), {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ iface }),
      });
      const data = await res.json();
      if (!res.ok || !data.ok) throw new Error(data && data.error ? data.error : "scan_failed");
      renderNetworkList(data.networks || []);
      setNetworkStatus(`${(data.networks || []).length} networks`);
    } catch (e) {
      renderNetworkList([]);
      setNetworkStatus(e && e.message ? e.message : "Scan failed");
    }
  }

  async function connectSelectedNetwork() {
    const iface = networkIface ? networkIface.value : "";
    const net = networkState.selectedNetwork;
    const ssid = net ? net.ssid : "";
    if (!iface || !ssid) {
      setNetworkStatus("Select a network");
      return;
    }
    const isOpen = !!(networkOpen && networkOpen.checked);
    setNetworkStatus(`Connecting ${iface}...`);
    try {
      const res = await apiFetch(getApiUrl("/api/network/connect"), {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          iface,
          ssid,
          password: isOpen || !networkPassword ? "" : networkPassword.value,
          hidden: !!(networkHidden && networkHidden.checked),
          force_control_iface: !!(networkForceControl && networkForceControl.checked),
          security: net && net.security ? net.security : "",
          bssid: net && net.bssid ? net.bssid : "",
        }),
      });
      const data = await res.json();
      if (!res.ok || !data.ok) throw new Error(data && data.error ? data.error : "connect_failed");
      if (data.status && Array.isArray(data.status.interfaces)) {
        networkState.interfaces = data.status.interfaces;
        networkStatusLoadedAt = Date.now();
        renderNetworkInterfaces();
      } else {
        await loadNetworkStatus({ force: true });
      }
      if (networkPassword) networkPassword.value = "";
      setNetworkStatus("Connected");
    } catch (e) {
      setNetworkStatus(e && e.message ? e.message : "Connect failed");
    }
  }

  async function disconnectNetwork() {
    const iface = networkIface ? networkIface.value : "";
    if (!iface) return;
    setNetworkStatus(`Disconnecting ${iface}...`);
    try {
      const res = await apiFetch(getApiUrl("/api/network/disconnect"), {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          iface,
          force_control_iface: !!(networkForceControl && networkForceControl.checked),
        }),
      });
      const data = await res.json();
      if (!res.ok || !data.ok) throw new Error(data && data.error ? data.error : "disconnect_failed");
      if (data.status && Array.isArray(data.status.interfaces)) {
        networkState.interfaces = data.status.interfaces;
        networkStatusLoadedAt = Date.now();
        renderNetworkInterfaces();
      } else {
        await loadNetworkStatus({ force: true });
      }
      setNetworkStatus("Disconnected");
    } catch (e) {
      setNetworkStatus(e && e.message ? e.message : "Disconnect failed");
    }
  }

  async function loadDiscordWebhook() {
    setSettingsStatus("Loading...");
    try {
      const url = getApiUrl("/api/settings/discord_webhook");
      const res = await apiFetch(url, { cache: "no-store" });
      const data = await res.json();
      if (!res.ok) {
        throw new Error(data && data.error ? data.error : "settings_failed");
      }
      if (discordWebhookInput)
        discordWebhookInput.value = String(data.url || "");
      setSettingsStatus(
        data.configured ? "Webhook configured" : "No webhook configured",
      );
    } catch (e) {
      setSettingsStatus("Failed to load settings");
    }
  }

  async function loadWigleSettings(skipLoadingState) {
    if (!wigleSettingsStatus) return;
    if (!skipLoadingState) setWigleStatus("Loading...");
    try {
      const url = getApiUrl("/api/settings/wigle");
      const res = await apiFetch(url, { cache: "no-store" });
      const data = await res.json();
      if (!res.ok) {
        throw new Error(data && data.error ? data.error : "wigle_failed");
      }
      applyWigleSettingsToUI(data);
      setWigleStatus(getWigleConfiguredStatus(data));
    } catch (e) {
      setWigleStatus(e && e.message ? e.message : "Failed to load WiGLE");
    }
  }

  function applyTailscaleDataToUI(data) {
    if (!tailscaleSettingsStatus) return;
    const installed = !!data.installed;
    const installing = !!data.installing;
    const backendState =
      data.backend_state || (installed ? "Unknown" : "Not installed");

    if (tailscaleInstallBtn) {
      const installingNow = !!installing && !installed;
      tailscaleInstallBtn.classList.toggle("hidden", installed);
      tailscaleInstallBtn.disabled = installingNow;
      tailscaleInstallBtn.classList.toggle("opacity-50", installingNow);
      tailscaleInstallBtn.classList.toggle("cursor-not-allowed", installingNow);
    }
    if (tailscaleReauthBtn) {
      const showReauth = installed;
      const disabledReauth = !!installing;
      tailscaleReauthBtn.classList.toggle("hidden", !showReauth);
      tailscaleReauthBtn.disabled = disabledReauth;
      tailscaleReauthBtn.classList.toggle("opacity-50", disabledReauth);
      tailscaleReauthBtn.classList.toggle("cursor-not-allowed", disabledReauth);
    }

    if (installing) {
      setTailscaleStatus("Installing Tailscale…");
    } else if (!installed) {
      setTailscaleStatus("Not installed");
    } else {
      setTailscaleStatus(`Installed (state: ${backendState || "Running"})`);
    }
  }

  async function loadTailscaleSettings(skipLoadingState) {
    if (!tailscaleSettingsStatus) return;
    if (!skipLoadingState) setTailscaleStatus("Loading...");
    try {
      const url = getApiUrl("/api/settings/tailscale");
      const res = await apiFetch(url, { cache: "no-store" });
      const data = await res.json();
      if (!res.ok) {
        throw new Error(data && data.error ? data.error : "tailscale_failed");
      }
      applyTailscaleDataToUI(data);
    } catch (e) {
      setTailscaleStatus("Failed to load Tailscale");
    }
  }

  function applyRuntimeConfig(data) {
    const values = (data && data.values) || {};
    const configured = (data && data.configured) || {};
    if (configApIface) configApIface.value = values.JACKPACK_AP_IFACE || "";
    if (configAttackIface) configAttackIface.value = values.JACKPACK_ATTACK_IFACE || "";
    if (configWiredIface) configWiredIface.value = values.JACKPACK_WIRED_IFACE || "";
    if (configApSsid) configApSsid.value = values.JACKPACK_AP_SSID || "";
    if (configApPassword) {
      configApPassword.value = "";
      configApPassword.placeholder = configured.JACKPACK_AP_PASSWORD
        ? `Saved: ${values.JACKPACK_AP_PASSWORD || "configured"}`
        : "New AP password";
    }
    if (configHostname) configHostname.value = values.JACKPACK_HOSTNAME || "";
    if (configApAddress) configApAddress.value = values.JACKPACK_AP_ADDRESS || "";
    if (configApChannel) configApChannel.value = values.JACKPACK_AP_CHANNEL || "";
    if (configWebPort) configWebPort.value = values.RJ_WEB_PORT || "";
    if (configWsPort) configWsPort.value = values.RJ_WS_PORT || "";
  }

  async function loadRuntimeConfig() {
    if (!configStatus) return;
    setConfigStatus("Loading...");
    try {
      const res = await apiFetch(getApiUrl("/api/settings/runtime"), { cache: "no-store" });
      const data = await res.json();
      if (!res.ok || !data.ok) throw new Error(data && data.error ? data.error : "config_failed");
      applyRuntimeConfig(data);
      setConfigStatus("Loaded");
    } catch (e) {
      setConfigStatus("Unavailable");
    }
  }

  async function saveRuntimeConfig() {
    const values = {
      JACKPACK_AP_IFACE: configApIface ? configApIface.value : "",
      JACKPACK_ATTACK_IFACE: configAttackIface ? configAttackIface.value : "",
      JACKPACK_WIRED_IFACE: configWiredIface ? configWiredIface.value : "",
      JACKPACK_AP_SSID: configApSsid ? configApSsid.value : "",
      JACKPACK_HOSTNAME: configHostname ? configHostname.value : "",
      JACKPACK_AP_ADDRESS: configApAddress ? configApAddress.value : "",
      JACKPACK_AP_CHANNEL: configApChannel ? configApChannel.value : "",
      RJ_WEB_PORT: configWebPort ? configWebPort.value : "",
      RJ_WS_PORT: configWsPort ? configWsPort.value : "",
    };
    if (configApPassword && configApPassword.value.trim()) {
      values.JACKPACK_AP_PASSWORD = configApPassword.value.trim();
    }
    setConfigStatus("Saving...");
    try {
      const res = await apiFetch(getApiUrl("/api/settings/runtime"), {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ values }),
      });
      const data = await res.json();
      if (!res.ok || !data.ok) throw new Error(data && data.error ? data.error : "save_failed");
      applyRuntimeConfig(data);
      setConfigStatus("Saved. Restart services to apply.");
    } catch (e) {
      setConfigStatus(e && e.message ? e.message : "Save failed");
    }
  }

  function renderUpdateStatus(data) {
    const running = !!(data && data.running);
    if (updateOutput) {
      updateOutput.textContent = (data && (data.output || data.message)) || "No update run yet.";
    }
    if (running) {
      setUpdateStatus("Updating...");
    } else if (data && data.ok === true) {
      const before = data.rev_before || "?";
      const after = data.rev_after || "?";
      setUpdateStatus(before === after ? "Already current" : `Updated ${before} -> ${after}`);
    } else if (data && data.ok === false) {
      setUpdateStatus("Update failed");
    } else {
      setUpdateStatus("Ready");
    }
  }

  async function loadUpdateStatus() {
    if (!updateStatus) return false;
    try {
      const res = await apiFetch(getApiUrl("/api/system/update-status"), { cache: "no-store" });
      const data = await res.json();
      if (!res.ok) throw new Error("update_status_failed");
      renderUpdateStatus(data);
      return !!data.running;
    } catch (e) {
      setUpdateStatus("Unavailable");
      return false;
    }
  }

  function hasInternetCandidate() {
    return (networkState.interfaces || []).some((item) => {
      const role = String(item.role || "");
      const state = String(item.state || "").toLowerCase();
      const ip = String(item.ipv4 || "");
      if (item.protected || role === "control_ap") return false;
      if (!ip || ip === "-") return false;
      return state.includes("connected") || role === "wired_target" || role === "attack_wifi";
    });
  }

  async function ensureInternetForUpdate() {
    const ifaces = await loadNetworkStatus({ silent: true, force: true });
    const ok = hasInternetCandidate(ifaces);
    if (updateNetworkHint) updateNetworkHint.classList.toggle("hidden", ok);
    if (ok) return true;
    setUpdateStatus("Connect first");
    if (updateOutput) {
      updateOutput.textContent = "No internet link detected on wlan1 or eth0.\n\nOpen Connect, join WiFi with wlan1 or plug Ethernet, then run update again.";
    }
    return false;
  }

  async function startUpdate(applyInstaller = false) {
    if (!(await ensureInternetForUpdate())) {
      return;
    }
    setUpdateStatus("Starting...");
    try {
      const res = await apiFetch(getApiUrl("/api/system/update"), {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ restart: false, apply_installer: !!applyInstaller }),
      });
      const data = await res.json();
      if (!res.ok || !data.ok) throw new Error(data && data.error ? data.error : "update_failed");
      pollUpdateUntilDone();
    } catch (e) {
      setUpdateStatus(e && e.message ? e.message : "Update failed");
    }
  }

  function pollUpdateUntilDone() {
    let tries = 0;
    const tick = async () => {
      tries += 1;
      const running = await loadUpdateStatus();
      if (running && tries < 240) {
        setTimeout(tick, 1500);
      }
    };
    tick();
  }

  async function restartWebUi() {
    setUpdateStatus("Restarting...");
    try {
      const res = await apiFetch(getApiUrl("/api/system/restart-ui"), { method: "POST" });
      const data = await res.json();
      if (!res.ok || !data.ok) throw new Error(data && data.error ? data.error : "restart_failed");
      setUpdateStatus("Restart requested");
    } catch (e) {
      setUpdateStatus(e && e.message ? e.message : "Restart failed");
    }
  }

  function diagnosticClasses(status) {
    if (status === "pass") return "jp-diag-pass";
    if (status === "fail") return "jp-diag-fail";
    return "jp-diag-warn";
  }

  function renderDiagnostics(data) {
    const counts = (data && data.counts) || {};
    if (diagnosticsSummary) {
      diagnosticsSummary.innerHTML = `
        <span class="jp-pill jp-pill-pass">${Number(counts.pass || 0)} pass</span>
        <span class="jp-pill jp-pill-warn">${Number(counts.warn || 0)} warn</span>
        <span class="jp-pill jp-pill-fail">${Number(counts.fail || 0)} fail</span>
      `;
    }
    if (diagnosticsList) {
      const checks = Array.isArray(data?.checks) ? data.checks : [];
      diagnosticsList.innerHTML = checks.length
        ? checks
            .map((check) => {
              const status = String(check.status || "warn");
              const icon = status === "pass" ? "check" : status === "fail" ? "xmark" : "triangle-exclamation";
              return `<div class="jp-diag-row ${diagnosticClasses(status)}">
                <div class="jp-diag-icon"><i class="fa-solid fa-${icon}"></i></div>
                <div class="min-w-0">
                  <div class="jp-diag-label">${escapeHtml(check.label || check.key || "Check")}</div>
                  <div class="jp-diag-detail">${escapeHtml(check.detail || "")}</div>
                </div>
              </div>`;
            })
            .join("")
        : '<div class="text-xs text-slate-500">No diagnostics loaded yet.</div>';
    }
    setDiagnosticsStatus(data && data.ready ? "Ready" : "Needs attention");
  }

  async function loadDiagnostics() {
    if (!diagnosticsStatus) return;
    setDiagnosticsStatus("Checking...");
    try {
      const res = await apiFetch(getApiUrl("/api/system/diagnostics"), { cache: "no-store" });
      const data = await res.json();
      if (!res.ok || !data.ok) throw new Error(data && data.error ? data.error : "diagnostics_failed");
      renderDiagnostics(data);
    } catch (e) {
      setDiagnosticsStatus("Unavailable");
      if (diagnosticsList) diagnosticsList.innerHTML = '<div class="text-xs text-rose-300">Diagnostics unavailable.</div>';
    }
  }

  async function saveDiscordWebhook(url) {
    setSettingsStatus("Saving...");
    try {
      const endpoint = getApiUrl("/api/settings/discord_webhook");
      const res = await apiFetch(endpoint, {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ url: String(url || "").trim() }),
      });
      const data = await res.json();
      if (!res.ok || !data.ok) {
        throw new Error(data && data.error ? data.error : "save_failed");
      }
      setSettingsStatus(
        data.status === "cleared" ? "Webhook cleared" : "Webhook saved",
      );
    } catch (e) {
      setSettingsStatus("Failed to save webhook");
    }
  }

  async function saveWigleSettings(apiName, apiToken, clearRequested) {
    setWigleStatus("Saving...");
    try {
      const endpoint = getApiUrl("/api/settings/wigle");
      const res = await apiFetch(endpoint, {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          api_name: String(apiName || "").trim(),
          api_token: String(apiToken || "").trim(),
          clear: !!clearRequested,
        }),
      });
      const data = await res.json();
      if (!res.ok || !data.ok) {
        throw new Error(data && data.error ? data.error : "save_failed");
      }
      applyWigleSettingsToUI(data);
      setWigleStatus(
        data.status === "cleared"
          ? "WiGLE cleared"
          : getWigleConfiguredStatus(data),
      );
    } catch (e) {
      setWigleStatus(e && e.message ? e.message : "Failed to save WiGLE");
    }
  }

  function openTailscaleModal() {
    if (!tailscaleModal) return;
    if (tailscaleKeyInput) tailscaleKeyInput.value = "";
    if (tailscaleModalError) {
      tailscaleModalError.textContent = "";
      tailscaleModalError.classList.add("hidden");
    }
    if (tailscaleModalStatus) tailscaleModalStatus.textContent = "";
    tailscaleModal.classList.remove("hidden");
    if (tailscaleKeyInput) tailscaleKeyInput.focus();
  }

  function closeTailscaleModal() {
    if (!tailscaleModal) return;
    tailscaleModal.classList.add("hidden");
  }

  let tailscaleInstallPollTimer = null;

  function startTailscaleInstallPoll() {
    if (tailscaleInstallPollTimer) clearInterval(tailscaleInstallPollTimer);
    const poll = async () => {
      try {
        const url = getApiUrl("/api/settings/tailscale");
        const res = await apiFetch(url, { cache: "no-store" });
        const data = await res.json();
        if (!res.ok) return;
        applyTailscaleDataToUI(data);
        const installed = !!data.installed;
        const installing = !!data.installing;
        if (installed && !installing) {
          clearInterval(tailscaleInstallPollTimer);
          tailscaleInstallPollTimer = null;
        }
      } catch (e) {
        // ignore poll errors; next interval will retry
      }
    };
    tailscaleInstallPollTimer = setInterval(poll, 2000);
    poll();
  }

  async function submitTailscaleInstall() {
    if (!tailscaleKeyInput) return;
    const key = String(tailscaleKeyInput.value || "").trim();
    if (!key) {
      if (tailscaleModalError) {
        tailscaleModalError.textContent = "Auth key required";
        tailscaleModalError.classList.remove("hidden");
      }
      return;
    }
    if (!key.startsWith("tskey-")) {
      if (tailscaleModalError) {
        tailscaleModalError.textContent = "Auth key must start with 'tskey-'.";
        tailscaleModalError.classList.remove("hidden");
      }
      return;
    }
    if (tailscaleModalError) {
      tailscaleModalError.textContent = "";
      tailscaleModalError.classList.add("hidden");
    }
    if (tailscaleModalStatus)
      tailscaleModalStatus.textContent = tailscaleReauthMode
        ? "Starting re-auth…"
        : "Starting install…";
    const setDisabled = (flag) => {
      if (tailscaleKeyInput) tailscaleKeyInput.disabled = flag;
      if (tailscaleModalSave) tailscaleModalSave.disabled = flag;
      if (tailscaleModalCancel) tailscaleModalCancel.disabled = flag;
    };
    setDisabled(true);
    try {
      const endpoint = getApiUrl("/api/settings/tailscale");
      const res = await apiFetch(endpoint, {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ auth_key: key, reauth: tailscaleReauthMode }),
      });
      const data = await res.json();
      if (!res.ok || !data.ok) {
        const msg = data && data.error ? data.error : "install_failed";
        throw new Error(msg);
      }
      if (tailscaleModalStatus)
        tailscaleModalStatus.textContent = tailscaleReauthMode
          ? "Re-authenticating…"
          : "Installing Tailscale…";
      closeTailscaleModal();
      setTailscaleStatus(
        tailscaleReauthMode ? "Re-authenticating…" : "Installing Tailscale…",
      );
      startTailscaleInstallPoll();
    } catch (e) {
      const msg = e && e.message ? e.message : "Failed to start install";
      if (tailscaleModalError) {
        tailscaleModalError.textContent = msg;
        tailscaleModalError.classList.remove("hidden");
      }
    } finally {
      setDisabled(false);
    }
  }

  function formatTime(ts) {
    try {
      const d = new Date(ts * 1000);
      return d.toLocaleString();
    } catch {
      return "";
    }
  }

  function buildLootPath(parent, name) {
    return parent ? `${parent}/${name}` : name;
  }

  function setLootStatus(text) {
    if (lootStatus) lootStatus.textContent = text;
  }

  function setLootPath(text) {
    if (lootPathEl) lootPathEl.textContent = text ? `/${text}` : "/";
  }

  function updateLootUp() {
    if (!lootUpBtn) return;
    const disabled = !lootState.path;
    lootUpBtn.disabled = disabled;
    lootUpBtn.classList.toggle("opacity-40", disabled);
    lootUpBtn.classList.toggle("cursor-not-allowed", disabled);
  }

  function openPreview({ title, content, meta, downloadUrl }) {
    if (!lootPreview) return;
    if (lootPreviewTitle) lootPreviewTitle.textContent = title || "Preview";
    if (lootPreviewBody) lootPreviewBody.textContent = content || "";
    if (lootPreviewMeta) lootPreviewMeta.textContent = meta || "";
    if (lootPreviewDownload) lootPreviewDownload.href = downloadUrl || "#";
    lootPreview.classList.remove("hidden");
  }

  function closePreview() {
    if (!lootPreview) return;
    lootPreview.classList.add("hidden");
  }

  function setNmapVizStatus(text) {
    if (!nmapVizStatus) return;
    nmapVizStatus.textContent = text || "Ready";
    applyStatusTone(nmapVizStatus, text || "Ready");
  }

  function setNmapVizError(message) {
    if (!nmapVizError) return;
    const text = String(message || "").trim();
    nmapVizError.textContent = text;
    nmapVizError.classList.toggle("hidden", !text);
  }

  function revokeNmapJsonUrl() {
    if (!nmapVizState.jsonUrl) return;
    try {
      URL.revokeObjectURL(nmapVizState.jsonUrl);
    } catch {}
    nmapVizState.jsonUrl = "";
  }

  function closeNmapViz() {
    if (!nmapVizModal) return;
    nmapVizModal.classList.add("hidden");
    setNmapVizError("");
    setNmapVizStatus("Ready");
  }

  function hasStructuredData(value) {
    if (Array.isArray(value)) return value.length > 0;
    if (value && typeof value === "object")
      return Object.keys(value).length > 0;
    return value !== null && value !== undefined && value !== "";
  }

  function formatSeverityLabel(value) {
    const text = String(value || "unknown").toLowerCase();
    return text.charAt(0).toUpperCase() + text.slice(1);
  }

  function getSeverityClasses(value) {
    const severity = String(value || "unknown").toLowerCase();
    if (severity === "critical")
      return "border-rose-400/30 bg-rose-500/15 text-rose-200";
    if (severity === "high")
      return "border-orange-400/30 bg-orange-500/15 text-orange-200";
    if (severity === "medium")
      return "border-amber-400/30 bg-amber-500/15 text-amber-200";
    if (severity === "low")
      return "border-sky-400/30 bg-sky-500/15 text-sky-200";
    return "border-slate-500/30 bg-slate-800/60 text-slate-300";
  }

  function formatScriptContext(script) {
    if (!script || !script.context) return "Host script";
    if (script.context.scope === "port") {
      const port = script.context.port ?? "?";
      const proto = script.context.protocol || "?";
      return `Port ${port}/${proto}`;
    }
    return "Host script";
  }

  function toPrettyJson(value) {
    try {
      return JSON.stringify(value, null, 2);
    } catch {
      return String(value || "");
    }
  }

  function isNmapLootXml(parentPath, name) {
    const current = String(parentPath || "");
    const fileName = String(name || "");
    return (
      /\.xml$/i.test(fileName) &&
      (current === "Nmap" || current.startsWith("Nmap/"))
    );
  }

  function renderNmapSummaryCards(data, hosts) {
    const hostCount = hosts.length;
    const upCount = hosts.filter(
      (host) => String((host && host.status) || "").toLowerCase() === "up",
    ).length;
    const portCount = hosts.reduce(
      (sum, host) =>
        sum + (host && Array.isArray(host.ports) ? host.ports.length : 0),
      0,
    );
    const vulnCount = hosts.reduce(
      (sum, host) =>
        sum +
        (host && Array.isArray(host.vulnerabilities)
          ? host.vulnerabilities.length
          : 0),
      0,
    );
    const elapsed =
      data && data.stats && data.stats.elapsed
        ? `${Number(data.stats.elapsed).toFixed(2)}s`
        : "Unknown";
    const cards = [
      { label: "Hosts", value: String(hostCount), tone: "text-emerald-200" },
      { label: "Up", value: String(upCount), tone: "text-cyan-200" },
      { label: "Ports", value: String(portCount), tone: "text-slate-100" },
      {
        label: "Vulnerabilities",
        value: String(vulnCount),
        tone: vulnCount ? "text-rose-200" : "text-slate-100",
      },
      { label: "Elapsed", value: elapsed, tone: "text-slate-100" },
    ];
    return `
      <div class="grid grid-cols-2 xl:grid-cols-5 gap-3">
        ${cards
          .map(
            (card) => `
          <div class="rounded-xl border border-slate-800/70 bg-slate-900/50 px-4 py-3">
            <div class="text-[11px] uppercase tracking-[0.18em] text-slate-500">${escapeHtml(card.label)}</div>
            <div class="mt-2 text-lg font-semibold ${card.tone}">${escapeHtml(card.value)}</div>
          </div>
        `,
          )
          .join("")}
      </div>
    `;
  }

  function renderVulnerabilityList(vulnerabilities) {
    if (!Array.isArray(vulnerabilities) || !vulnerabilities.length) {
      return '<div class="text-xs text-slate-500">No vulnerabilities identified.</div>';
    }
    return vulnerabilities
      .map((vuln) => {
        const refs = Array.isArray(vuln.references) ? vuln.references : [];
        const portLabel = vuln.port
          ? ` · Port ${escapeHtml(String(vuln.port))}/${escapeHtml(String(vuln.protocol || "?"))}`
          : "";
        return `
        <div class="rounded-xl border ${getSeverityClasses(vuln.severity)} px-3 py-3">
          <div class="flex flex-wrap items-center gap-2">
            <span class="text-xs font-semibold">${escapeHtml(vuln.id || "Finding")}</span>
            <span class="px-2 py-0.5 rounded-full border text-[10px] ${getSeverityClasses(vuln.severity)}">${escapeHtml(formatSeverityLabel(vuln.severity))}</span>
            <span class="text-[11px] text-slate-400">${escapeHtml(vuln.source_script_id || "script")}${portLabel}</span>
          </div>
          <div class="mt-2 text-xs text-slate-100 whitespace-pre-wrap">${escapeHtml(vuln.description || "No description available.")}</div>
          ${refs.length ? `<div class="mt-2 text-[11px] text-slate-400">Refs: ${escapeHtml(refs.join(", "))}</div>` : ""}
        </div>
      `;
      })
      .join("");
  }

  function renderPortList(ports) {
    if (!Array.isArray(ports) || !ports.length) {
      return '<div class="text-xs text-slate-500">No port data in this scan.</div>';
    }
    return `
      <div class="space-y-2">
        ${ports
          .map((port) => {
            const serviceBits = [
              port.service,
              port.product,
              port.version,
            ].filter(Boolean);
            return `
            <div class="rounded-xl border border-slate-800/70 bg-slate-900/40 px-3 py-3">
              <div class="flex flex-wrap items-center justify-between gap-2">
                <div class="text-sm text-slate-100 font-medium">${escapeHtml(String(port.port ?? "?"))}/${escapeHtml(String(port.protocol || "?"))}</div>
                <div class="flex flex-wrap items-center gap-2">
                  <span class="px-2 py-0.5 rounded-full border text-[10px] ${String(port.state || "").toLowerCase() === "open" ? "border-emerald-400/30 bg-emerald-500/10 text-emerald-200" : "border-slate-600/40 bg-slate-800/70 text-slate-300"}">${escapeHtml(String(port.state || "unknown"))}</span>
                  ${port.scripts && port.scripts.length ? `<span class="text-[11px] text-slate-400">${escapeHtml(String(port.scripts.length))} scripts</span>` : ""}
                </div>
              </div>
              <div class="mt-2 text-xs text-slate-300">${escapeHtml(serviceBits.join(" · ") || "Service metadata unavailable")}</div>
              ${port.extrainfo ? `<div class="mt-1 text-[11px] text-slate-500">${escapeHtml(String(port.extrainfo))}</div>` : ""}
            </div>
          `;
          })
          .join("")}
      </div>
    `;
  }

  function renderOsSection(osInfo) {
    if (
      !osInfo ||
      (!osInfo.name &&
        !(Array.isArray(osInfo.matches) && osInfo.matches.length))
    ) {
      return '<div class="text-xs text-slate-500">No OS detection data in this scan.</div>';
    }
    const matches = Array.isArray(osInfo.matches)
      ? osInfo.matches.slice(0, 3)
      : [];
    return `
      <div class="space-y-2">
        <div class="rounded-xl border border-slate-800/70 bg-slate-900/40 px-3 py-3">
          <div class="text-sm font-medium text-slate-100">${escapeHtml(String(osInfo.name || "Best match unavailable"))}</div>
          <div class="mt-1 text-[11px] text-slate-400">Accuracy: ${escapeHtml(String(osInfo.accuracy ?? "unknown"))}</div>
        </div>
        ${matches
          .map(
            (match) => `
          <div class="rounded-xl border border-slate-800/70 bg-slate-950/40 px-3 py-2">
            <div class="text-xs text-slate-200">${escapeHtml(String(match.name || "Unknown match"))}</div>
            <div class="text-[11px] text-slate-500">Accuracy ${escapeHtml(String(match.accuracy ?? "unknown"))}</div>
          </div>
        `,
          )
          .join("")}
      </div>
    `;
  }

  function renderScriptOutputs(scripts) {
    if (!Array.isArray(scripts) || !scripts.length) {
      return '<div class="text-xs text-slate-500">No script output in this scan.</div>';
    }
    return scripts
      .map((script) => {
        const structured = hasStructuredData(script.structured)
          ? `<div class="mt-3"><div class="text-[11px] uppercase tracking-[0.16em] text-slate-500 mb-1">Structured</div><pre class="text-[11px] text-cyan-100 whitespace-pre-wrap rounded-lg border border-slate-800/70 bg-slate-950/70 p-3 overflow-auto">${escapeHtml(toPrettyJson(script.structured))}</pre></div>`
          : "";
        const vulnerabilities =
          Array.isArray(script.vulnerabilities) && script.vulnerabilities.length
            ? `<div class="mt-3 space-y-2">${renderVulnerabilityList(script.vulnerabilities)}</div>`
            : "";
        return `
        <details class="rounded-xl border border-slate-800/70 bg-slate-900/45 px-3 py-3 group">
          <summary class="flex flex-wrap items-center gap-2 cursor-pointer list-none">
            <span class="text-xs font-semibold text-slate-100">${escapeHtml(String(script.id || "script"))}</span>
            <span class="text-[11px] text-slate-400">${escapeHtml(formatScriptContext(script))}</span>
            ${script.is_vulnerability ? `<span class="px-2 py-0.5 rounded-full border text-[10px] border-rose-400/30 bg-rose-500/15 text-rose-200">Vulnerability</span>` : ""}
          </summary>
          <div class="mt-3 text-[11px] uppercase tracking-[0.16em] text-slate-500 mb-1">Raw Output</div>
          <pre class="text-[11px] text-slate-100 whitespace-pre-wrap rounded-lg border border-slate-800/70 bg-slate-950/70 p-3 overflow-auto">${escapeHtml(String(script.output || "No raw output available."))}</pre>
          ${structured}
          ${vulnerabilities}
        </details>
      `;
      })
      .join("");
  }

  function renderHostCard(host) {
    const hostnames =
      Array.isArray(host.hostnames) && host.hostnames.length
        ? host.hostnames.join(", ")
        : "No hostnames";
    const ports = Array.isArray(host.ports) ? host.ports : [];
    const vulnerabilities = Array.isArray(host.vulnerabilities)
      ? host.vulnerabilities
      : [];
    const scripts = Array.isArray(host.raw_scripts) ? host.raw_scripts : [];
    const highest =
      host && host.severity_summary ? host.severity_summary.highest : null;
    return `
      <section class="rounded-2xl border border-slate-800/70 bg-slate-950/45 overflow-hidden">
        <div class="px-4 py-4 border-b border-slate-800/70 bg-slate-900/45">
          <div class="flex flex-wrap items-center gap-2">
            <div class="text-base font-semibold text-slate-100">${escapeHtml(String(host.ip || "Unknown host"))}</div>
            <span class="px-2 py-0.5 rounded-full border text-[10px] ${String(host.status || "").toLowerCase() === "up" ? "border-emerald-400/30 bg-emerald-500/10 text-emerald-200" : "border-slate-600/40 bg-slate-800/70 text-slate-300"}">${escapeHtml(String(host.status || "unknown"))}</span>
            ${highest ? `<span class="px-2 py-0.5 rounded-full border text-[10px] ${getSeverityClasses(highest)}">${escapeHtml(formatSeverityLabel(highest))}</span>` : ""}
          </div>
          <div class="mt-2 text-xs text-slate-400">${escapeHtml(hostnames)}</div>
          <div class="mt-2 flex flex-wrap gap-3 text-[11px] text-slate-500">
            <span>MAC: ${escapeHtml(String(host.mac || "n/a"))}</span>
            <span>Vendor: ${escapeHtml(String(host.vendor || "n/a"))}</span>
            <span>Ports: ${escapeHtml(String(ports.length))}</span>
            <span>Findings: ${escapeHtml(String(vulnerabilities.length))}</span>
          </div>
        </div>
        <div class="grid xl:grid-cols-2 gap-4 p-4">
          <div>
            <div class="text-[11px] uppercase tracking-[0.18em] text-slate-500 mb-2">Ports & Services</div>
            ${renderPortList(ports)}
          </div>
          <div>
            <div class="text-[11px] uppercase tracking-[0.18em] text-slate-500 mb-2">OS Detection</div>
            ${renderOsSection(host.os)}
          </div>
        </div>
        <div class="grid xl:grid-cols-2 gap-4 px-4 pb-4">
          <div>
            <div class="text-[11px] uppercase tracking-[0.18em] text-slate-500 mb-2">Vulnerabilities</div>
            ${renderVulnerabilityList(vulnerabilities)}
          </div>
          <div>
            <div class="text-[11px] uppercase tracking-[0.18em] text-slate-500 mb-2">Script Outputs</div>
            <div class="space-y-2">${renderScriptOutputs(scripts)}</div>
          </div>
        </div>
      </section>
    `;
  }

  function renderNmapVisualization() {
    if (!nmapVizBody) return;
    const data = nmapVizState.data;
    if (!data) {
      nmapVizBody.innerHTML =
        '<div class="text-sm text-slate-400">No Nmap data loaded.</div>';
      return;
    }

    const allHosts = Array.isArray(data.hosts) ? data.hosts : [];
    const vulnerableOnly = !!(nmapVizFilterVuln && nmapVizFilterVuln.checked);
    const hosts = vulnerableOnly
      ? allHosts.filter(
          (host) =>
            Array.isArray(host.vulnerabilities) && host.vulnerabilities.length,
        )
      : allHosts;
    const warnings = Array.isArray(data.warnings) ? data.warnings : [];
    const args = data && data.scan ? data.scan.args : "";
    const rawXmlSection = data.raw_xml
      ? `<details class="rounded-xl border border-slate-800/70 bg-slate-900/45 px-4 py-3"><summary class="cursor-pointer text-xs font-semibold text-slate-200">Raw XML</summary><pre class="mt-3 text-[11px] text-slate-100 whitespace-pre-wrap rounded-lg border border-slate-800/70 bg-slate-950/70 p-3 overflow-auto">${escapeHtml(String(data.raw_xml || ""))}</pre></details>`
      : "";
    const warningsSection = warnings.length
      ? `<div class="rounded-xl border border-amber-400/20 bg-amber-500/10 px-4 py-3 text-xs text-amber-100">Warnings: ${escapeHtml(warnings.join(" | "))}</div>`
      : "";

    nmapVizBody.innerHTML = `
      ${renderNmapSummaryCards(data, hosts)}
      ${args ? `<div class="rounded-xl border border-slate-800/70 bg-slate-900/45 px-4 py-3 text-xs text-slate-300"><span class="text-slate-500 uppercase tracking-[0.16em] mr-2">Args</span>${escapeHtml(String(args))}</div>` : ""}
      ${warningsSection}
      <div class="space-y-4">
        ${hosts.length ? hosts.map(renderHostCard).join("") : '<div class="rounded-xl border border-slate-800/70 bg-slate-900/45 px-4 py-6 text-sm text-slate-400">No hosts match the current filter.</div>'}
      </div>
      ${rawXmlSection}
    `;
  }

  async function loadNmapVisualization(path, name) {
    if (!nmapVizModal) return;
    const xmlUrl = getApiUrl("/api/loot/download", { path });
    if (nmapVizTitle) nmapVizTitle.textContent = name || "Nmap Visualization";
    if (nmapVizMeta) nmapVizMeta.textContent = path ? `/${path}` : "";
    if (nmapVizDownloadXml) nmapVizDownloadXml.href = xmlUrl;
    if (nmapVizFilterVuln) nmapVizFilterVuln.checked = false;
    setNmapVizError("");
    setNmapVizStatus("Loading...");
    nmapVizState.data = null;
    revokeNmapJsonUrl();
    if (nmapVizBody)
      nmapVizBody.innerHTML =
        '<div class="text-sm text-slate-400">Parsing XML and normalizing results...</div>';
    nmapVizModal.classList.remove("hidden");

    try {
      const url = getApiUrl("/api/loot/nmap", { path, include_raw: "1" });
      const res = await apiFetch(url, { cache: "no-store" });
      const data = await res.json();
      if (!res.ok) {
        throw new Error(
          data && data.error ? data.error : "Failed to parse Nmap XML",
        );
      }
      nmapVizState.data = data;
      if (nmapVizMeta) {
        const metaBits = [
          path ? `/${path}` : "",
          data && data.scan && data.scan.version
            ? `Nmap ${data.scan.version}`
            : "",
          data && data.stats && data.stats.time_str ? data.stats.time_str : "",
        ].filter(Boolean);
        nmapVizMeta.textContent = metaBits.join(" · ");
      }
      if (nmapVizDownloadJson) {
        const jsonBlob = new Blob([JSON.stringify(data, null, 2)], {
          type: "application/json",
        });
        nmapVizState.jsonUrl = URL.createObjectURL(jsonBlob);
        nmapVizDownloadJson.href = nmapVizState.jsonUrl;
        nmapVizDownloadJson.download = String(name || "nmap").replace(
          /\.xml$/i,
          ".json",
        );
      }
      renderNmapVisualization();
      setNmapVizStatus("Ready");
    } catch (e) {
      setNmapVizStatus("Parse failed");
      setNmapVizError(e && e.message ? e.message : "Failed to parse Nmap XML");
      if (nmapVizBody)
        nmapVizBody.innerHTML =
          '<div class="text-sm text-slate-400">The XML file could not be visualized.</div>';
    }
  }

  function renderLoot(items) {
    if (!lootList) return;
    if (!items.length) {
      lootList.innerHTML =
        '<div class="px-3 py-4 text-sm text-slate-400">No files found.</div>';
      return;
    }
    const rows = items
      .map((item) => {
        const itemType = item && item.type === "dir" ? "dir" : "file";
        const icon = itemType === "dir" ? "📁" : "📄";
        const meta =
          itemType === "dir"
            ? "Folder"
            : `${formatBytes(item.size)} · ${formatTime(item.mtime)}`;
        const safeName = escapeHtml(item.name || "");
        const encodedName = encodeData(item.name || "");
        const vizAction = isNmapLootXml(lootState.path, item.name)
          ? `<span role="button" tabindex="0" title="Visualize Nmap XML" aria-label="Visualize Nmap XML" data-visualize-nmap="${encodedName}" class="ml-2 inline-flex h-6 w-6 items-center justify-center rounded-md border border-emerald-400/20 bg-emerald-500/10 text-emerald-200 hover:bg-emerald-500/20 transition align-middle"><i class="fa-solid fa-network-wired pointer-events-none text-[11px]"></i></span>`
          : "";
        return `
        <button class="w-full text-left px-3 py-2 flex items-center gap-3 hover:bg-slate-800/60 transition loot-item" data-type="${itemType}" data-name="${encodedName}">
          <span class="text-lg">${icon}</span>
          <div class="flex-1 min-w-0">
            <div class="text-sm text-slate-100 truncate"><span>${safeName}</span>${vizAction}</div>
            <div class="text-[11px] text-slate-400">${escapeHtml(meta)}</div>
          </div>
          <div class="text-xs text-slate-400">${itemType === "dir" ? "Open" : "Download"}</div>
        </button>
      `;
      })
      .join("");
    lootList.innerHTML = rows;
  }

  async function loadLoot(path = "") {
    setLootStatus("Loading...");
    try {
      const url = getApiUrl("/api/loot/list", { path });
      const res = await apiFetch(url, { cache: "no-store" });
      const data = await res.json();
      if (!res.ok) {
        throw new Error(data && data.error ? data.error : "Failed to load");
      }
      lootState = { path: data.path || "", parent: data.parent || "" };
      setLootPath(lootState.path);
      updateLootUp();
      renderLoot(data.items || []);
      setLootStatus("Ready");
    } catch (e) {
      setLootStatus("Failed to load loot");
      renderLoot([]);
    }
  }

  async function previewLootFile(path, name) {
    setLootStatus("Loading preview...");
    try {
      const url = getApiUrl("/api/loot/view", { path });
      const res = await apiFetch(url, { cache: "no-store" });
      const data = await res.json();
      if (!res.ok) {
        throw new Error(data && data.error ? data.error : "preview_failed");
      }
      const meta = `${formatBytes(data.size || 0)} · ${formatTime(data.mtime || 0)}${data.truncated ? " · truncated" : ""}`;
      const downloadUrl = getApiUrl("/api/loot/download", { path });
      openPreview({
        title: name,
        content: data.content || "",
        meta,
        downloadUrl,
      });
      setLootStatus("Ready");
    } catch (e) {
      setLootStatus("Preview unavailable");
      const downloadUrl = getApiUrl("/api/loot/download", { path });
      window.open(downloadUrl, "_blank");
    }
  }

  async function loadPayloads() {
    setPayloadStatus("Loading...");
    try {
      payloadState.schemaCache = {};
      const url = getApiUrl("/api/payloads/list");
      const res = await apiFetch(url, { cache: "no-store" });
      const data = await res.json();
      if (!res.ok) {
        throw new Error(data && data.error ? data.error : "payloads_failed");
      }
      payloadState.categories = data.categories || [];
      payloadState.categories.forEach((cat, idx) => {
        if (payloadState.open[cat.id] === undefined) {
          payloadState.open[cat.id] = idx === 0;
        }
      });
      if (!payloadState.selectedCategory && payloadState.categories.length) {
        payloadState.selectedCategory = payloadState.categories[0].id || "";
      }
      renderPayloadSidebar();
      renderPayloadCategories();
      renderPayloadQuickGrid();
      if (!payloadState.selectedPath) {
        renderPayloadDetail(null);
      }
      setPayloadStatus("Ready");
    } catch (e) {
      setPayloadStatus("Failed to load");
      if (payloadSidebar)
        payloadSidebar.innerHTML =
          '<div class="text-xs text-slate-500 px-2">No payloads available.</div>';
      if (payloadQuickGrid)
        payloadQuickGrid.innerHTML =
          '<div class="text-xs text-slate-500">No payloads available.</div>';
      if (payloadCategoryList)
        payloadCategoryList.innerHTML =
          '<div class="text-xs text-slate-500">No categories available.</div>';
    }
  }

  async function createNativePayload() {
    const title = payloadCreatorName ? payloadCreatorName.value.trim() : "";
    if (!title) {
      setPayloadCreatorStatus("Name required");
      if (payloadCreatorName) payloadCreatorName.focus();
      return;
    }
    setPayloadCreatorStatus("Creating...");
    try {
      const res = await apiFetch(getApiUrl("/api/payloads/native"), {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          title,
          description: payloadCreatorDescription ? payloadCreatorDescription.value : "",
          iface_kind: payloadCreatorIface ? payloadCreatorIface.value : "none",
          fields: payloadCreatorFields ? payloadCreatorFields.value : "",
        }),
      });
      const data = await res.json();
      if (!res.ok || !data.ok) {
        throw new Error(data && data.error ? data.error : "create_failed");
      }
      setPayloadCreatorStatus("Created");
      if (payloadCreatorName) payloadCreatorName.value = "";
      if (payloadCreatorDescription) payloadCreatorDescription.value = "";
      if (payloadCreatorFields) payloadCreatorFields.value = "";
      payloadState.schemaCache = {};
      await loadPayloads();
      if (data.path) selectPayload(data.path, { scroll: true });
    } catch (e) {
      setPayloadCreatorStatus(e && e.message ? e.message : "Create failed");
    }
  }

  function renderPayloadSidebar() {
    if (!payloadSidebar) return;
    const cats = payloadState.categories || [];
    if (!cats.length) {
      payloadSidebar.innerHTML =
        '<div class="text-xs text-slate-500 px-2">No categories.</div>';
      return;
    }
    payloadSidebar.innerHTML = cats
      .map((cat) => {
        const catId = String(cat?.id || "");
        const catIdEncoded = encodeData(catId);
        const catLabel = escapeHtml(String(cat?.label || catId || "Category"));
        const isSelected = payloadState.selectedCategory === catId;
        const count = Array.isArray(cat.items) ? cat.items.length : 0;
        return `
        <button type="button" data-cat="${catIdEncoded}" class="w-full px-3 py-2 text-left text-xs font-semibold flex items-center justify-between rounded-lg border ${isSelected ? "border-emerald-400/40 bg-emerald-500/10 text-emerald-200" : "border-slate-800/70 bg-slate-950/40 text-slate-300"}">
            <span>${catLabel}</span>
            <span class="text-slate-500">${count}</span>
        </button>
      `;
      })
      .join("");
  }

  function allPayloadItems() {
    const items = [];
    (payloadState.categories || []).forEach((cat) => {
      (cat.items || []).forEach((item) => {
        items.push({ ...item, category: cat.label || cat.id || "Payloads", categoryId: cat.id || "" });
      });
    });
    return items;
  }

  function selectPayloadCategory(id) {
    const cats = payloadState.categories || [];
    payloadState.selectedCategory = id || (cats[0] && cats[0].id) || "";
    renderPayloadSidebar();
    renderPayloadCategories();
    renderPayloadQuickGrid();
    scrollIntoWorkbench(payloadBrowserPanel);
  }

  function renderPayloadCategories() {
    if (!payloadCategoryList) return;
    const cats = payloadState.categories || [];
    if (!cats.length) {
      payloadCategoryList.innerHTML = '<div class="text-xs text-slate-500">No payload categories.</div>';
      return;
    }
    payloadCategoryList.innerHTML = cats
      .map((cat) => {
        const id = String(cat.id || "");
        const selected = id === payloadState.selectedCategory;
        const count = Array.isArray(cat.items) ? cat.items.length : 0;
        return `<button type="button" data-payload-category="${encodeData(id)}" class="jp-category-card ${selected ? "jp-category-active" : ""}">
          <span class="jp-category-title">${escapeHtml(cat.label || id || "Category")}</span>
          <span class="jp-category-count">${count}</span>
        </button>`;
      })
      .join("");
  }

  function renderPayloadQuickGrid() {
    if (!payloadQuickGrid) return;
    const cats = payloadState.categories || [];
    if (!payloadState.selectedCategory && cats.length) {
      payloadState.selectedCategory = cats[0].id || "";
    }
    const selectedCat = cats.find((cat) => cat.id === payloadState.selectedCategory) || cats[0] || null;
    const query = String(payloadState.query || "").trim().toLowerCase();
    let items = query
      ? allPayloadItems()
      : (selectedCat?.items || []).map((item) => ({
          ...item,
          category: selectedCat.label || selectedCat.id || "Payloads",
          categoryId: selectedCat.id || "",
        }));
    if (query) {
      items = items.filter((item) => {
        const meta = item.meta || {};
        const haystack = [
          item.name,
          item.path,
          item.category,
          meta.description,
          ...(Array.isArray(meta.tags) ? meta.tags : []),
        ]
          .join(" ")
          .toLowerCase();
        return haystack.includes(query);
      });
    }
    const total = allPayloadItems().length;
    if (payloadSummary) {
      payloadSummary.innerHTML = `<span>${total} native payload${total === 1 ? "" : "s"}</span>`;
    }
    if (payloadCategoryTitle) {
      payloadCategoryTitle.textContent = query
        ? `Search Results`
        : selectedCat
          ? selectedCat.label || "Payloads"
          : "Payloads";
    }
    if (payloadCategoryDescription) {
      payloadCategoryDescription.textContent = query
        ? `${items.length} matches for "${payloadState.query}"`
        : selectedCat
          ? selectedCat.description || `${items.length} payloads`
          : "Select a category.";
    }
    if (!items.length) {
      payloadQuickGrid.innerHTML = '<div class="jp-empty-form">No payloads match this view.</div>';
      return;
    }
    payloadQuickGrid.innerHTML = items
      .map((item) => {
        const itemPath = String(item.path || "");
        const encoded = encodeData(itemPath);
        const meta = item.meta || {};
        const tags = Array.isArray(meta.tags) && meta.tags.length ? meta.tags : [String(item.category || "payload")];
        const description = meta.description || "No description.";
        const isActive = payloadState.activePath === itemPath;
        const isSelected = payloadState.selectedPath === itemPath;
        const action = isActive
          ? '<span class="jp-pill-danger"><i class="fa-solid fa-stop"></i> Running</span>'
          : `<span class="jp-payload-open">${isSelected ? "Selected" : "Open"}</span>`;
        return `
          <div class="jp-payload-card ${isSelected ? "jp-payload-selected" : ""}" data-select-payload="${encoded}">
            <div class="jp-payload-row">
              <div class="min-w-0">
                <div class="jp-payload-name">${escapeHtml(payloadLabel(itemPath))}</div>
                <div class="jp-payload-path">${escapeHtml(itemPath)}</div>
                <div class="jp-payload-desc">${escapeHtml(description)}</div>
                <div class="jp-tag-row jp-tag-row-compact">${tags.slice(0, 3).map((tag, idx) => `<span class="jp-tag ${idx === 0 ? "jp-tag-purple" : ""}">${escapeHtml(String(tag))}</span>`).join("")}</div>
              </div>
              ${action}
            </div>
          </div>
        `;
      })
      .join("");
  }

  function splitArgs(text) {
    const args = [];
    let cur = "";
    let quote = "";
    let escaped = false;
    for (const char of String(text || "")) {
      if (escaped) {
        cur += char;
        escaped = false;
      } else if (char === "\\") {
        escaped = true;
      } else if (quote) {
        if (char === quote) quote = "";
        else cur += char;
      } else if (char === '"' || char === "'") {
        quote = char;
      } else if (/\s/.test(char)) {
        if (cur) {
          args.push(cur);
          cur = "";
        }
      } else {
        cur += char;
      }
    }
    if (cur) args.push(cur);
    return args;
  }

  function payloadFieldHtml(field, idx) {
    const name = escapeHtml(field.name || `field_${idx}`);
    const label = escapeHtml(field.label || field.name || "Option");
    const help = field.help ? `<div class="jp-field-help">${escapeHtml(field.help)}</div>` : "";
    const required = field.required ? "required" : "";
    const envAttr = field.env ? `data-env="${escapeHtml(field.env)}"` : "";
    const def = field.default === undefined || field.default === null ? "" : String(field.default);
    if (field.type === "textarea") {
      return `<label class="jp-field jp-field-wide">
        <span>${label}</span>
        <textarea data-payload-field="${name}" data-arg="${escapeHtml(field.arg || "")}" ${envAttr} ${required} rows="${escapeHtml(field.rows || 4)}">${escapeHtml(def)}</textarea>
        ${help}
      </label>`;
    }
    if (field.type === "checkbox") {
      const checked = field.default === true ? "checked" : "";
      return `<label class="jp-check-row">
        <input type="checkbox" data-payload-field="${name}" data-arg="${escapeHtml(field.arg || "")}" ${envAttr} ${checked}>
        <span><strong>${label}</strong>${help}</span>
      </label>`;
    }
    if (field.type === "interface") {
      const ifaceType = String(field.iface_type || "").toLowerCase();
      const needsMonitor = !!field.require_monitor;
      const allowControl = field.allow_control_iface === true;
      const interfaces = (networkState.interfaces || []).filter((item) => {
        if (!(item.present || item.recommended || item.protected)) return false;
        if (!allowControl && (item.protected || item.role === "control_ap")) return false;
        if (ifaceType === "wifi") return !!item.wireless;
        if (ifaceType === "eth" || ifaceType === "wired") return !item.wireless;
        if (needsMonitor) return !!item.wireless;
        return true;
      });
      const options = interfaces.length
        ? interfaces.map((item) => {
            const value = String(item.name || "");
            const selected = value === def ? "selected" : "";
            return `<option value="${escapeHtml(value)}" ${selected}>${escapeHtml(ifaceLabel(item))}</option>`;
          }).join("")
        : `<option value="${escapeHtml(def || "wlan1")}">${escapeHtml(def || "wlan1")}</option>`;
      return `<label class="jp-field">
        <span>${label}</span>
        <select data-payload-field="${name}" data-arg="${escapeHtml(field.arg || "")}" ${envAttr} ${required}>
          ${options}
        </select>
        ${help}
      </label>`;
    }
    if (field.type === "select" && Array.isArray(field.choices)) {
      return `<label class="jp-field">
        <span>${label}</span>
        <select data-payload-field="${name}" data-arg="${escapeHtml(field.arg || "")}" ${envAttr} ${required}>
          <option value="">Default</option>
          ${field.choices.map((choice) => `<option value="${escapeHtml(choice)}" ${choice === def ? "selected" : ""}>${escapeHtml(choice)}</option>`).join("")}
        </select>
        ${help}
      </label>`;
    }
    if (field.type === "portal_select") {
      const portals = Array.isArray(payloadState.workflow?.portals) && payloadState.workflow.portals.length
        ? payloadState.workflow.portals
        : [{ id: "", label: "Built-in WiFi Login" }];
      return `<label class="jp-field">
        <span>${label}</span>
        <select data-payload-field="${name}" data-arg="${escapeHtml(field.arg || "")}" ${envAttr} ${required}>
          ${portals.map((portal) => {
            const value = String(portal.id || "");
            const selected = value === def ? "selected" : "";
            return `<option value="${escapeHtml(value)}" ${selected}>${escapeHtml(portal.label || value || "Built-in WiFi Login")}</option>`;
          }).join("")}
        </select>
        ${help}
      </label>`;
    }
    const minAttr = field.min === undefined || field.min === null ? "" : `min="${escapeHtml(field.min)}"`;
    const maxAttr = field.max === undefined || field.max === null ? "" : `max="${escapeHtml(field.max)}"`;
    return `<label class="jp-field">
      <span>${label}</span>
      <input type="${field.type === "number" ? "number" : "text"}" data-payload-field="${name}" data-arg="${escapeHtml(field.arg || "")}" ${envAttr} value="${escapeHtml(def)}" ${required} ${minAttr} ${maxAttr}>
      ${help}
    </label>`;
  }

  function renderPayloadFormInto(container, schema, rawInput, emptyText) {
    if (!container) return;
    const fields = Array.isArray(schema?.fields) ? schema.fields : [];
    if (!fields.length) {
      container.innerHTML = `<div class="jp-empty-form">${escapeHtml(emptyText || "No structured options declared. Raw args are available below.")}</div>`;
    } else {
      container.innerHTML = fields.map((field, idx) => payloadFieldHtml(field, idx)).join("");
    }
    if (rawInput) rawInput.value = "";
  }

  function workflowForSelectedSchema() {
    const schema = payloadState.selectedSchema || payloadState.activeSchema || {};
    return schema.workflow && typeof schema.workflow === "object" ? schema.workflow : null;
  }

  function renderWorkflowAuthorization(workflow) {
    if (!workflow || !workflow.requires_authorization) return "";
    return `<label class="jp-check-row jp-auth-row">
      <input type="checkbox" data-workflow-authorized>
      <span><strong>Authorized test</strong><small>I have explicit permission to run this workflow on the selected target(s).</small></span>
    </label>`;
  }

  function renderWifiTargetRows() {
    const networks = Array.isArray(payloadState.workflow.networks) ? payloadState.workflow.networks : [];
    if (!networks.length) {
      return '<div class="jp-empty-form">No AP scan loaded yet. Pick the external WiFi adapter, then press Scan APs.</div>';
    }
    return networks
      .map((net) => {
        const bssid = String(net.bssid || "");
        const ssid = String(net.ssid || net.essid || "(hidden)");
        const signal = net.signal === null || net.signal === undefined ? "-" : `${net.signal}%`;
        const channel = String(net.channel || "");
        const security = String(net.security || "");
        const checked = payloadState.workflow.selectedBssids?.[bssid] ? "checked" : "";
        return `<label class="jp-target-row">
          <input type="checkbox" data-wifi-target
            data-ssid="${escapeHtml(ssid)}"
            data-bssid="${escapeHtml(bssid)}"
            data-channel="${escapeHtml(channel)}"
            data-signal="${escapeHtml(net.signal ?? "")}"
            ${checked}>
          <span class="min-w-0">
            <strong>${escapeHtml(ssid)}</strong>
            <small>${escapeHtml([bssid, channel ? `ch ${channel}` : "", security].filter(Boolean).join(" · "))}</small>
          </span>
          <em>${escapeHtml(signal)}</em>
        </label>`;
      })
      .join("");
  }

  function renderPayloadWorkflow(schema) {
    const workflow = schema?.workflow;
    if (!workflow || !payloadInlineForm) return false;
    if (payloadInlineRawWrap) payloadInlineRawWrap.classList.add("hidden");
    const formSchema = { fields: Array.isArray(workflow.fields) ? workflow.fields : [] };
    renderPayloadFormInto(payloadInlineForm, formSchema, null, "This workflow does not need setup fields.");
    if (workflow.type === "wifi_ap_targets") {
      payloadInlineForm.insertAdjacentHTML(
        "beforeend",
        `${renderWorkflowAuthorization(workflow)}
        <div class="jp-workflow-box">
          <div class="flex items-center justify-between gap-2">
            <div>
              <div class="jp-mini-title">Targets</div>
              <div class="jp-panel-subtitle">Scan APs, then select one or more authorized test targets.</div>
            </div>
            <button type="button" class="jp-btn" data-workflow-scan-wifi><i class="fa-solid fa-magnifying-glass"></i> ${escapeHtml(workflow.scan_label || "Scan APs")}</button>
          </div>
          <div class="jp-target-list mt-3">${renderWifiTargetRows()}</div>
        </div>`,
      );
      return true;
    }
    if (workflow.type === "captive_portal") {
      payloadInlineForm.insertAdjacentHTML("beforeend", renderWorkflowAuthorization(workflow));
      if (!payloadState.workflow.portals.length) {
        loadWorkflowPortals().catch(() => {});
      }
      return true;
    }
    if (payloadInlineRawWrap) payloadInlineRawWrap.classList.remove("hidden");
    return false;
  }

  function workflowFieldEnv(formEl = payloadInlineForm) {
    return buildPayloadArgsFromForm(formEl, null).env || {};
  }

  function selectedIfaceIsControl(iface) {
    const name = String(iface || "").trim();
    if (!name) return false;
    return (networkState.interfaces || []).some((item) => (
      String(item.name || "") === name && (item.protected || item.role === "control_ap")
    ));
  }

  async function loadWorkflowPortals() {
    const res = await apiFetch(getApiUrl("/api/payloads/workflow/portals"), { cache: "no-store" });
    const data = await res.json();
    if (!res.ok || !data.ok) throw new Error(data && data.error ? data.error : "portal_load_failed");
    payloadState.workflow.portals = Array.isArray(data.portals) ? data.portals : [];
    if (payloadState.selectedSchema?.workflow?.type === "captive_portal") {
      renderPayloadDetail(payloadState.selectedSchema);
    }
  }

  async function scanWorkflowWifiTargets() {
    const workflow = workflowForSelectedSchema();
    if (!workflow || workflow.type !== "wifi_ap_targets") return;
    const env = workflowFieldEnv();
    const iface = env.JACKPACK_SELECTED_IFACE || env.JACKPACK_ATTACK_IFACE || "wlan1";
    if (payloadInlineStatus) payloadInlineStatus.textContent = `Scanning ${iface}...`;
    payloadState.workflow.status = `Scanning ${iface}...`;
    try {
      const res = await apiFetch(getApiUrl("/api/network/scan"), {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ iface }),
      });
      const data = await res.json();
      if (!res.ok || !data.ok) throw new Error(data && data.error ? data.error : "scan_failed");
      payloadState.workflow.networks = Array.isArray(data.networks) ? data.networks : [];
      payloadState.workflow.selectedBssids = {};
      if (payloadInlineStatus) {
        payloadInlineStatus.textContent = `${payloadState.workflow.networks.length} AP${payloadState.workflow.networks.length === 1 ? "" : "s"} found.`;
      }
      payloadState.workflow.status = payloadState.workflow.networks.length
        ? `${payloadState.workflow.networks.length} AP${payloadState.workflow.networks.length === 1 ? "" : "s"} found. Select authorized targets, then launch.`
        : "No APs found. Try a longer scan time or another adapter.";
      renderPayloadDetail(payloadState.selectedSchema);
    } catch (e) {
      payloadState.workflow.status = e && e.message ? e.message : "Scan failed";
      if (payloadInlineStatus) payloadInlineStatus.textContent = payloadState.workflow.status;
    }
  }

  function selectedWifiTargetsFromDom() {
    if (!payloadInlineForm) return [];
    return Array.from(payloadInlineForm.querySelectorAll("[data-wifi-target]:checked"))
      .map((el) => {
        const signalRaw = el.getAttribute("data-signal") || "";
        let power = -99;
        if (/^-?\d+$/.test(signalRaw)) {
          const signal = Number(signalRaw);
          power = signal > 0 ? Math.round((signal / 2) - 100) : signal;
        }
        return {
          ssid: el.getAttribute("data-ssid") || "",
          essid: el.getAttribute("data-ssid") || "",
          bssid: el.getAttribute("data-bssid") || "",
          channel: el.getAttribute("data-channel") || "",
          signal: signalRaw,
          power,
          clients: 0,
        };
      })
      .filter((item) => item.bssid && item.channel);
  }

  function buildWorkflowLaunch(schema) {
    const workflow = schema?.workflow;
    if (!workflow) return null;
    const env = workflowFieldEnv();
    const authorized = !workflow.requires_authorization || !!payloadInlineForm?.querySelector("[data-workflow-authorized]")?.checked;
    if (!authorized) {
      return { ok: false, error: "Confirm this is an authorized test first." };
    }
    const selectedIface = env.JACKPACK_SELECTED_IFACE || env.JACKPACK_ATTACK_IFACE || "";
    if (selectedIfaceIsControl(selectedIface)) {
      return { ok: false, error: `${selectedIface} is the JackPack control AP. Choose the USB WiFi adapter.` };
    }
    if (workflow.type === "wifi_ap_targets") {
      const targets = selectedWifiTargetsFromDom();
      if (!targets.length) {
        return { ok: false, error: "Select at least one AP target first." };
      }
      env[workflow.target_env || "JACKPACK_DEAUTH_TARGETS"] = JSON.stringify(targets);
      env[workflow.autostart_env || "JACKPACK_DEAUTH_AUTOSTART"] = "1";
      return { ok: true, args: [], env };
    }
    if (workflow.type === "captive_portal") {
      env[workflow.autostart_env || "JACKPACK_CAPTIVE_PORTAL_AUTOSTART"] = "1";
      if (!env.JACKPACK_CAPTIVE_PORTAL_SSID) {
        return { ok: false, error: "Enter a portal SSID first." };
      }
      return { ok: true, args: [], env };
    }
    return null;
  }

  function handleWorkflowFormChange(e) {
    const target = e.target;
    if (!target || !target.matches("[data-wifi-target]")) return;
    const bssid = target.getAttribute("data-bssid") || "";
    if (!bssid) return;
    payloadState.workflow.selectedBssids[bssid] = !!target.checked;
  }

  function handleWorkflowFormClick(e) {
    const scanBtn = e.target.closest("[data-workflow-scan-wifi]");
    if (scanBtn) {
      scanWorkflowWifiTargets();
    }
  }

  function renderPayloadDetail(schema) {
    const path = String(schema?.path || payloadState.selectedPath || "");
    const meta = schema?.meta || {};
    const selected = !!path;
    const tags = Array.isArray(meta.tags) && meta.tags.length ? meta.tags : [];
    if (payloadDetailTitle) {
      payloadDetailTitle.textContent = selected ? (schema?.name || payloadLabel(path)) : "None selected";
    }
    if (payloadDetailPath) {
      payloadDetailPath.textContent = selected ? path : "Pick from the list on the left.";
    }
    if (payloadDetailDescription) {
      const workflowSummary = schema?.workflow?.summary || "";
      payloadDetailDescription.textContent = selected
        ? (workflowSummary || meta.description || "This payload does not describe itself yet. Setup and inferred controls are shown below.")
        : "Select a payload.";
    }
    if (payloadDetailTags) {
      payloadDetailTags.innerHTML = selected
        ? tags.slice(0, 6).map((tag, idx) => `<span class="jp-tag ${idx === 0 ? "jp-tag-purple" : ""}">${escapeHtml(String(tag))}</span>`).join("")
        : "";
    }
    const hasWorkflow = renderPayloadWorkflow(schema);
    if (!hasWorkflow) {
      if (payloadInlineRawWrap) payloadInlineRawWrap.classList.remove("hidden");
      renderPayloadFormInto(
        payloadInlineForm,
        schema,
        payloadInlineRaw,
        selected
          ? "No setup fields were detected for this payload yet. Launch with defaults, or add raw args if the payload supports CLI flags."
          : "Select a payload to see setup fields.",
      );
    }
    if (payloadInlineStatus) {
      const fieldCount = Array.isArray((hasWorkflow ? schema?.workflow?.fields : schema?.fields)) ? (hasWorkflow ? schema.workflow.fields.length : schema.fields.length) : 0;
      payloadInlineStatus.textContent = selected
        ? hasWorkflow
          ? (payloadState.workflow.status || schema?.workflow?.summary || "Configure, then launch.")
          : fieldCount
            ? `${fieldCount} setup field${fieldCount === 1 ? "" : "s"} ready.`
            : "Launches with defaults."
        : "Select a payload first.";
    }
    if (payloadInlineLaunch) {
      payloadInlineLaunch.disabled = !selected || !!payloadState.activePath;
      payloadInlineLaunch.innerHTML = payloadState.activePath === path
        ? '<i class="fa-solid fa-circle-play"></i> Running'
        : '<i class="fa-solid fa-play"></i> Launch';
    }
    renderPayloadActions();
  }

  function scrollIntoWorkbench(el) {
    if (!el) return;
    setTimeout(() => {
      try {
        el.scrollIntoView({ behavior: "smooth", block: "start" });
      } catch {
        el.scrollIntoView();
      }
    }, 40);
  }

  async function selectPayload(path, opts = {}) {
    const cleanPath = String(path || "");
    if (!cleanPath) return;
    if (payloadState.workflow.path !== cleanPath) {
      payloadState.workflow = { path: cleanPath, networks: [], selectedBssids: {}, portals: [], status: "" };
    }
    payloadState.selectedPath = cleanPath;
    if (payloadInlineStatus) payloadInlineStatus.textContent = "Loading setup...";
    if (payloadInlineLaunch) payloadInlineLaunch.disabled = true;
    if (payloadDetailTitle) payloadDetailTitle.textContent = payloadLabel(cleanPath);
    if (payloadDetailPath) payloadDetailPath.textContent = cleanPath;
    if (payloadInlineForm) payloadInlineForm.innerHTML = '<div class="jp-empty-form">Loading setup...</div>';
    if (payloadInlineRawWrap) payloadInlineRawWrap.classList.add("hidden");
    renderPayloadQuickGrid();
    if (opts.scroll) scrollIntoWorkbench(payloadDetailPanel);
    try {
      let schema = payloadState.schemaCache[cleanPath];
      if (!schema) {
        const res = await apiFetch(getApiUrl("/api/payloads/schema", { path: cleanPath }), { cache: "no-store" });
        schema = await res.json();
        if (!res.ok) throw new Error(schema && schema.error ? schema.error : "schema_failed");
        payloadState.schemaCache[cleanPath] = schema;
      }
      const schemaFields = Array.isArray(schema.fields) ? schema.fields : [];
      const workflowFields = Array.isArray(schema.workflow?.fields) ? schema.workflow.fields : [];
      const needsInterfaces = [...schemaFields, ...workflowFields].some((field) => field && field.type === "interface");
      payloadState.selectedSchema = schema;
      if (payloadState.activePath === cleanPath) {
        payloadState.activeSchema = schema;
      }
      renderPayloadDetail(schema);
      if (needsInterfaces && !networkState.interfaces.length) {
        loadNetworkStatus({ silent: true }).then(() => {
          if (payloadState.selectedPath === cleanPath) renderPayloadDetail(schema);
        });
      }
    } catch (e) {
      payloadState.selectedSchema = { path: cleanPath, name: payloadLabel(cleanPath), fields: [], raw_args: true, actions: [], meta: { description: "No setup metadata yet." } };
      renderPayloadDetail(payloadState.selectedSchema);
      if (payloadInlineStatus) payloadInlineStatus.textContent = e && e.message ? e.message : "Setup unavailable";
    }
  }

  async function loadActivePayloadSchema(path) {
    if (!path) {
      payloadState.activeSchema = null;
      renderPayloadActions();
      return;
    }
    if (payloadState.activeSchema && payloadState.activeSchema.path === path) {
      renderPayloadActions();
      return;
    }
    try {
      const res = await apiFetch(getApiUrl("/api/payloads/schema", { path }), { cache: "no-store" });
      const schema = await res.json();
      if (!res.ok) throw new Error(schema && schema.error ? schema.error : "schema_failed");
      payloadState.activeSchema = schema;
      if (!payloadState.selectedPath || payloadState.selectedPath === path) {
        payloadState.selectedPath = path;
        payloadState.selectedSchema = schema;
        renderPayloadDetail(schema);
      }
    } catch {
      payloadState.activeSchema = { path, actions: [] };
    }
    renderPayloadActions();
  }

  function buildPayloadArgsFromForm(formEl = null, rawEl = null) {
    const args = [];
    const env = {};
    if (formEl) {
      formEl.querySelectorAll("[data-payload-field]").forEach((el) => {
        const arg = el.getAttribute("data-arg") || "";
        const envKey = el.getAttribute("data-env") || "";
        if (el.type === "checkbox") {
          if (envKey) env[envKey] = el.checked ? "1" : "0";
          else if (arg && el.checked) args.push(arg);
          return;
        }
        const value = String(el.value || "").trim();
        if (!value) return;
        if (envKey) env[envKey] = value;
        else if (arg) args.push(arg, value);
      });
    }
    if (rawEl && rawEl.value.trim()) {
      args.push(...splitArgs(rawEl.value));
    }
    return { args, env };
  }

  async function confirmInlinePayloadLaunch() {
    const path = payloadState.selectedPath;
    if (!path) return;
    const workflowLaunch = buildWorkflowLaunch(payloadState.selectedSchema);
    if (workflowLaunch) {
      if (!workflowLaunch.ok) {
        if (payloadInlineStatus) payloadInlineStatus.textContent = workflowLaunch.error || "Workflow is incomplete.";
        payloadState.workflow.status = workflowLaunch.error || "Workflow is incomplete.";
        return;
      }
      payloadState.activeSchema = payloadState.selectedSchema || null;
      await startPayload(path, workflowLaunch.args, workflowLaunch.env);
      scrollIntoWorkbench(payloadDetailPanel);
      return;
    }
    const built = buildPayloadArgsFromForm(payloadInlineForm, payloadInlineRaw);
    payloadState.activeSchema = payloadState.selectedSchema || null;
    await startPayload(path, built.args, built.env);
    scrollIntoWorkbench(payloadDetailPanel);
  }

  async function startPayload(path, args = [], env = {}) {
    setPayloadStatus("Starting...");
    if (payloadLogTail) payloadLogTail.textContent = "Starting payload...";
    if (payloadWorkbenchLogTail) payloadWorkbenchLogTail.textContent = "Starting payload...";
    payloadState.activePath = path;
    payloadState.selectedPath = path;
    setActivePayloadView({ running: true, path, started_at: Date.now() / 1000 });
    try {
      const url = getApiUrl("/api/payloads/start");
      const res = await apiFetch(url, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ path, args, env }),
      });
      const data = await res.json();
      if (!res.ok || !data.ok) {
        throw new Error(data && data.error ? data.error : "start_failed");
      }
      payloadState.activePath = path;
      payloadState.selectedPath = path;
      setActivePayloadView(data);
      if (!payloadState.activeSchema || payloadState.activeSchema.path !== path) {
        await loadActivePayloadSchema(path);
      } else {
        renderPayloadActions();
      }
      renderPayloadSidebar();
      renderPayloadQuickGrid();
      renderPayloadDetail(payloadState.selectedSchema || payloadState.activeSchema || { path, meta: {}, fields: [], actions: [] });
      setPayloadStatus("Launched");
      loadPayloadLog();
    } catch (e) {
      payloadState.activePath = null;
      setActivePayloadView({ running: false, path: null });
      renderPayloadQuickGrid();
      renderPayloadDetail(payloadState.selectedSchema);
      setPayloadStatus(e && e.message ? e.message : "Start failed");
    }
  }

  async function stopPayload() {
    setPayloadStatus("Stopping...");
    try {
      const url = getApiUrl("/api/payloads/stop");
      const res = await apiFetch(url, { method: "POST" });
      const data = await res.json();
      if (!res.ok || !data.ok) {
        throw new Error(data && data.error ? data.error : "stop_failed");
      }
      payloadState.activePath = null;
      payloadState.activeSchema = null;
      setActivePayloadView({ running: false, path: null });
      renderPayloadSidebar();
      renderPayloadQuickGrid();
      renderPayloadActions();
      renderPayloadDetail(payloadState.selectedSchema);
      setPayloadStatus("Ready");
      loadPayloadLog();
    } catch (e) {
      tapInput("KEY3");
      setPayloadStatus("Stop requested");
    }
  }

  async function pollPayloadStatus() {
    try {
      const url = getApiUrl("/api/payloads/status");
      const res = await apiFetch(url, { cache: "no-store" });
      const data = await res.json();
      if (!res.ok) {
        return;
      }
      const running = !!data.running;
      const path = running ? data.path || null : null;
      if (payloadState.activePath !== path) {
        payloadState.activePath = path;
        if (path) {
          payloadState.selectedPath = path;
          payloadState.selectedSchema = null;
        }
        payloadState.activeSchema = null;
        renderPayloadSidebar();
        renderPayloadQuickGrid();
      }
      if (running) {
        loadActivePayloadSchema(path);
      } else if (payloadState.activeSchema) {
        payloadState.activeSchema = null;
        renderPayloadActions();
      }
      setPayloadStatus(running ? "Running" : "Ready");
      setActivePayloadView(data);
    } catch (e) {
      setPayloadStatus("Ready");
    }
  }

  async function loadPayloadLog(force = false) {
    if (!payloadLogTail && !payloadWorkbenchLogTail) return;
    if (!force && !payloadState.activePath) {
      const idleText = "No active payload. Start one from the Payloads page.";
      if (payloadLogTail) payloadLogTail.textContent = idleText;
      if (payloadWorkbenchLogTail) payloadWorkbenchLogTail.textContent = idleText;
      setPayloadLogStatus("Idle");
      return;
    }
    setPayloadLogStatus("Loading...");
    try {
      const url = getApiUrl("/api/payloads/log", { bytes: "65536" });
      const res = await apiFetch(url, { cache: "no-store" });
      const data = await res.json();
      if (!res.ok) throw new Error(data && data.error ? data.error : "log_failed");
      const text = String(data.text || "").trim();
      const display = text || "No log output yet.";
      if (payloadLogTail) {
        payloadLogTail.textContent = display;
        payloadLogTail.scrollTop = payloadLogTail.scrollHeight;
      }
      if (payloadWorkbenchLogTail) {
        payloadWorkbenchLogTail.textContent = display;
        payloadWorkbenchLogTail.scrollTop = payloadWorkbenchLogTail.scrollHeight;
      }
      setPayloadLogStatus(data.exists ? "Live tail" : "No log yet");
    } catch (e) {
      if (payloadLogTail) payloadLogTail.textContent = "Unable to read payload log.";
      if (payloadWorkbenchLogTail) payloadWorkbenchLogTail.textContent = "Unable to read payload log.";
      setPayloadLogStatus("Unavailable");
    }
  }

  function handleTextSession(msg) {
    const active = !!(msg && msg.active);
    if (!active) {
      textSessionState = { active: false, sessionId: "", defaultValue: "" };
      if (payloadTextModal) payloadTextModal.classList.add("hidden");
      return;
    }
    const sessionId = String(msg.session_id || "");
    const defaultValue = String(msg.default || "");
    textSessionState = {
      active: true,
      sessionId,
      defaultValue,
    };
    if (payloadTextTitle) payloadTextTitle.textContent = msg.title || "Payload Input";
    if (payloadTextMeta) {
      const maxLen = Number(msg.max_len || 0);
      payloadTextMeta.textContent = maxLen ? `Maximum ${maxLen} characters` : "Runtime text request";
    }
    if (payloadTextInput && payloadTextInput.value === "") {
      payloadTextInput.value = defaultValue;
    }
    if (payloadTextModal) payloadTextModal.classList.remove("hidden");
    setTimeout(() => {
      try {
        payloadTextInput && payloadTextInput.focus();
        payloadTextInput && payloadTextInput.select();
      } catch {}
    }, 30);
  }

  function sendTextKey(payload) {
    if (!textSessionState.active || !textSessionState.sessionId) return;
    if (!ws || ws.readyState !== WebSocket.OPEN) return;
    try {
      ws.send(JSON.stringify({ type: "text_key", session_id: textSessionState.sessionId, ...payload }));
    } catch {}
  }

  function submitPayloadText() {
    if (!payloadTextInput) return;
    const value = String(payloadTextInput.value || "");
    const existing = String(textSessionState.defaultValue || "");
    for (let i = 0; i < existing.length; i += 1) {
      sendTextKey({ special: "BACKSPACE" });
    }
    for (const char of value) {
      sendTextKey({ key: char });
    }
    sendTextKey({ special: "ENTER" });
    payloadTextInput.value = "";
    if (payloadTextModal) payloadTextModal.classList.add("hidden");
  }

  function cancelPayloadText() {
    sendTextKey({ special: "ESCAPE" });
    if (payloadTextInput) payloadTextInput.value = "";
    if (payloadTextModal) payloadTextModal.classList.add("hidden");
  }

  function payloadTextBackspaceOnce() {
    sendTextKey({ special: "BACKSPACE" });
    if (payloadTextInput) {
      payloadTextInput.value = payloadTextInput.value.slice(0, -1);
    }
  }

  function sendInput(button, state) {
    if (!ws || ws.readyState !== WebSocket.OPEN) return;
    try {
      ws.send(JSON.stringify({ type: "input", button, state }));
    } catch {}
  }

  function tapInput(button) {
    sendInput(button, "press");
    setTimeout(() => sendInput(button, "release"), 120);
  }

  // Mouse/touch buttons
  function bindButtons() {
    const buttons = document.querySelectorAll("[data-btn]");
    buttons.forEach((btn) => {
      const name = btn.getAttribute("data-btn");
      const press = () => {
        btn.classList.add("active");
        sendInput(name, "press");
      };
      const release = () => {
        btn.classList.remove("active");
        sendInput(name, "release");
      };
      btn.addEventListener("mousedown", press);
      btn.addEventListener("mouseup", release);
      btn.addEventListener("mouseleave", release);
      btn.addEventListener(
        "touchstart",
        (e) => {
          e.preventDefault();
          press();
        },
        { passive: false },
      );
      btn.addEventListener(
        "touchend",
        (e) => {
          e.preventDefault();
          release();
        },
        { passive: false },
      );
      btn.addEventListener(
        "touchcancel",
        (e) => {
          e.preventDefault();
          release();
        },
        { passive: false },
      );
    });
  }

  // Keyboard mapping
  const KEYMAP = new Map([
    ["ArrowUp", "UP"],
    ["ArrowDown", "DOWN"],
    ["ArrowLeft", "LEFT"],
    ["ArrowRight", "RIGHT"],
    ["Enter", "OK"],
    ["NumpadEnter", "OK"],
    ["Digit1", "KEY1"],
    ["Digit2", "KEY2"],
    ["Digit3", "KEY3"],
    ["Escape", "KEY3"],
  ]);

  function bindKeyboard() {
    const isTypingFocus = () => {
      const el = document.activeElement;
      if (!el) return false;
      const tag = String(el.tagName || "").toUpperCase();
      return (
        tag === "INPUT" ||
        tag === "TEXTAREA" ||
        tag === "SELECT" ||
        !!el.isContentEditable
      );
    };

    window.addEventListener("keydown", (e) => {
      if (terminalHasFocus || isTypingFocus()) return;
      const btn = KEYMAP.get(e.code) || KEYMAP.get(e.key);
      if (!btn) return;
      if (pressed.has(btn)) return; // avoid repeats
      pressed.add(btn);
      sendInput(btn, "press");
      e.preventDefault();
    });
    window.addEventListener("keyup", (e) => {
      if (terminalHasFocus || isTypingFocus()) return;
      const btn = KEYMAP.get(e.code) || KEYMAP.get(e.key);
      if (!btn) return;
      pressed.delete(btn);
      sendInput(btn, "release");
      e.preventDefault();
    });
    window.addEventListener("blur", () => {
      // Release everything on blur to avoid stuck keys
      for (const btn of pressed) {
        sendInput(btn, "release");
      }
      pressed.clear();
    });
  }

  bindButtons();
  bindKeyboard();
  if (shellConnectBtn) shellConnectBtn.addEventListener("click", sendShellOpen);
  if (shellDisconnectBtn)
    shellDisconnectBtn.addEventListener("click", sendShellClose);
  document.querySelectorAll("[data-shell-command]").forEach((btn) => {
    btn.addEventListener("click", () => {
      const command = btn.getAttribute("data-shell-command") || "";
      sendShellCommand(command);
    });
  });
  if (logoutBtn) logoutBtn.addEventListener("click", logoutUser);
  document.addEventListener("click", (e) => {
    const btn = e.target.closest("[data-jp-tab]");
    if (!btn) return;
    const tab = btn.getAttribute("data-jp-tab");
    if (!tab) return;
    setActiveTab(tab);
    if (tab === "network") loadNetworkStatus({ force: true });
    if (tab === "payloads" && !payloadState.categories.length) loadPayloads();
    if (tab === "settings") {
      loadRuntimeConfig();
      loadUpdateStatus();
      loadDiagnostics();
      loadDiscordWebhook();
      loadWigleSettings();
      loadTailscaleSettings();
    }
  });
  window.addEventListener("resize", () => {
    if (shellOpen) sendShellResize();
  });
  if (navDevice)
    navDevice.addEventListener("click", () => setActiveTab("device"));
  if (navSystem)
    navSystem.addEventListener("click", () => {
      setSystemOpen(!systemOpen);
    });
  if (navNetwork)
    navNetwork.addEventListener("click", () => {
      setActiveTab("network");
      loadNetworkStatus();
    });
  if (navPayloads)
    navPayloads.addEventListener("click", () => {
      setActiveTab("payloads");
      if (!payloadState.categories.length) loadPayloads();
    });
  if (navTerminal)
    navTerminal.addEventListener("click", () => {
      setActiveTab("terminal");
      sendShellOpen();
    });
  if (navLoot)
    navLoot.addEventListener("click", () => {
      setActiveTab("loot");
      if (lootList && !lootList.dataset.loaded) {
        loadLoot("");
        lootList.dataset.loaded = "1";
      }
    });
  if (navSettings)
    navSettings.addEventListener("click", () => {
      setActiveTab("settings");
      loadRuntimeConfig();
      loadUpdateStatus();
      loadDiagnostics();
      loadDiscordWebhook();
      loadWigleSettings();
      loadTailscaleSettings();
    });
  document.querySelectorAll("[data-mobile-tab]").forEach((btn) => {
    btn.addEventListener("click", () => {
      const tab = btn.getAttribute("data-mobile-tab");
      if (!tab) return;
      setActiveTab(tab);
      if (tab === "network") loadNetworkStatus();
      if (tab === "payloads") loadPayloads();
      if (tab === "terminal") sendShellOpen();
      if (tab === "settings") {
        loadRuntimeConfig();
        loadUpdateStatus();
        loadDiagnostics();
        loadDiscordWebhook();
        loadWigleSettings();
        loadTailscaleSettings();
      }
      if (tab === "loot" && lootList && !lootList.dataset.loaded) {
        loadLoot("");
        lootList.dataset.loaded = "1";
      }
    });
  });
  if (menuToggle)
    menuToggle.addEventListener("click", () => setSidebarOpen(true));
  if (sidebarBackdrop)
    sidebarBackdrop.addEventListener("click", () => setSidebarOpen(false));
  if (lootUpBtn)
    lootUpBtn.addEventListener("click", () => {
      if (lootState.parent !== undefined) {
        loadLoot(lootState.parent || "");
      }
    });
  if (lootList)
    lootList.addEventListener("click", (e) => {
      const vizBtn = e.target.closest("[data-visualize-nmap]");
      if (vizBtn) {
        e.preventDefault();
        const encodedViz = vizBtn.getAttribute("data-visualize-nmap") || "";
        const vizName = decodeURIComponent(encodedViz);
        const vizPath = buildLootPath(lootState.path, vizName);
        loadNmapVisualization(vizPath, vizName);
        return;
      }
      const btn = e.target.closest(".loot-item");
      if (!btn) return;
      const encoded = btn.getAttribute("data-name") || "";
      const name = decodeURIComponent(encoded);
      const type = btn.getAttribute("data-type");
      const nextPath = buildLootPath(lootState.path, name);
      if (type === "dir") {
        loadLoot(nextPath);
      } else {
        previewLootFile(nextPath, name);
      }
    });
  if (payloadSidebar)
    payloadSidebar.addEventListener("click", (e) => {
      const catBtn = e.target.closest("[data-cat]");
      if (catBtn) {
        const encodedId = catBtn.getAttribute("data-cat") || "";
        const id = decodeURIComponent(encodedId);
        if (id) {
          setActiveTab("payloads");
          selectPayloadCategory(id);
        }
        return;
      }
      const startBtn = e.target.closest("[data-start]");
      if (startBtn) {
        const encodedPath = startBtn.getAttribute("data-start") || "";
        const path = decodeURIComponent(encodedPath);
        if (path) selectPayload(path, { scroll: true });
        return;
      }
      const stopBtn = e.target.closest("[data-stop]");
      if (stopBtn) {
        stopPayload();
      }
    });
  if (payloadsRefresh)
    payloadsRefresh.addEventListener("click", () => loadPayloads());
  if (payloadsRefreshMain)
    payloadsRefreshMain.addEventListener("click", () => {
      setActiveTab("payloads");
      loadPayloads();
    });
  if (payloadLibraryRefresh)
    payloadLibraryRefresh.addEventListener("click", () => loadPayloads());
  if (payloadLibraryStop)
    payloadLibraryStop.addEventListener("click", () => stopPayload());
  if (payloadWorkbenchStop)
    payloadWorkbenchStop.addEventListener("click", () => stopPayload());
  if (payloadSearch)
    payloadSearch.addEventListener("input", () => {
      payloadState.query = payloadSearch.value || "";
      renderPayloadQuickGrid();
    });
  if (payloadCategoryList)
    payloadCategoryList.addEventListener("click", (e) => {
      const btn = e.target.closest("[data-payload-category]");
      if (!btn) return;
      const id = decodeURIComponent(btn.getAttribute("data-payload-category") || "");
      selectPayloadCategory(id);
    });
  if (payloadQuickGrid)
    payloadQuickGrid.addEventListener("click", (e) => {
      const stopBtn = e.target.closest("[data-stop]");
      if (stopBtn) {
        stopPayload();
        return;
      }
      const selectBtn = e.target.closest("[data-select-payload]");
      if (selectBtn) {
        const encodedPath = selectBtn.getAttribute("data-select-payload") || "";
        const path = decodeURIComponent(encodedPath);
        if (path) selectPayload(path, { scroll: true });
        return;
      }
    });
  if (payloadInlineLaunch)
    payloadInlineLaunch.addEventListener("click", confirmInlinePayloadLaunch);
  if (payloadCreatorCreate)
    payloadCreatorCreate.addEventListener("click", createNativePayload);
  if (payloadInlineForm) {
    payloadInlineForm.addEventListener("click", handleWorkflowFormClick);
    payloadInlineForm.addEventListener("change", handleWorkflowFormChange);
  }
  if (payloadActionGrid)
    payloadActionGrid.addEventListener("click", (e) => {
      const btn = e.target.closest("[data-payload-action]");
      if (!btn || btn.disabled) return;
      const button = btn.getAttribute("data-payload-action") || "";
      if (button) tapInput(button);
    });
  if (payloadLogRefresh)
    payloadLogRefresh.addEventListener("click", () => loadPayloadLog(true));
  if (payloadWorkbenchLogRefresh)
    payloadWorkbenchLogRefresh.addEventListener("click", () => loadPayloadLog(true));
  if (activePayloadStop)
    activePayloadStop.addEventListener("click", () => stopPayload());
  if (networkRefresh)
    networkRefresh.addEventListener("click", () => loadNetworkStatus({ force: true }));
  if (networkScan)
    networkScan.addEventListener("click", () => scanNetworks());
  if (networkDisconnect)
    networkDisconnect.addEventListener("click", () => disconnectNetwork());
  if (networkConnect)
    networkConnect.addEventListener("click", () => connectSelectedNetwork());
  if (networkList)
    networkList.addEventListener("click", (e) => {
      const btn = e.target.closest("[data-network-index]");
      if (!btn) return;
      try {
        const items = JSON.parse(networkList.dataset.networks || "[]");
        const idx = Number(btn.getAttribute("data-network-index"));
        selectNetwork(items[idx]);
      } catch {}
    });
  if (networkOpen)
    networkOpen.addEventListener("change", () => {
      if (networkPassword) networkPassword.disabled = networkOpen.checked;
    });
  if (payloadTextSubmit)
    payloadTextSubmit.addEventListener("click", submitPayloadText);
  if (payloadTextCancel)
    payloadTextCancel.addEventListener("click", cancelPayloadText);
  if (payloadTextCancelTop)
    payloadTextCancelTop.addEventListener("click", cancelPayloadText);
  if (payloadTextBackspace)
    payloadTextBackspace.addEventListener("click", payloadTextBackspaceOnce);
  if (payloadTextInput)
    payloadTextInput.addEventListener("keydown", (e) => {
      if (e.key === "Enter") {
        e.preventDefault();
        submitPayloadText();
      } else if (e.key === "Escape") {
        e.preventDefault();
        cancelPayloadText();
      }
    });
  if (configReload)
    configReload.addEventListener("click", loadRuntimeConfig);
  if (configSave)
    configSave.addEventListener("click", saveRuntimeConfig);
  if (updateRefreshNetwork)
    updateRefreshNetwork.addEventListener("click", () => ensureInternetForUpdate());
  if (updatePull)
    updatePull.addEventListener("click", () => startUpdate(false));
  if (updateApply)
    updateApply.addEventListener("click", () => startUpdate(true));
  if (updateRestart)
    updateRestart.addEventListener("click", restartWebUi);
  if (diagnosticsRun)
    diagnosticsRun.addEventListener("click", loadDiagnostics);
  if (discordWebhookSave)
    discordWebhookSave.addEventListener("click", () => {
      saveDiscordWebhook(discordWebhookInput ? discordWebhookInput.value : "");
    });
  if (discordWebhookClear)
    discordWebhookClear.addEventListener("click", () => {
      if (discordWebhookInput) discordWebhookInput.value = "";
      saveDiscordWebhook("");
    });
  if (wigleSave)
    wigleSave.addEventListener("click", () => {
      saveWigleSettings(
        wigleApiNameInput ? wigleApiNameInput.value : "",
        wigleApiTokenInput ? wigleApiTokenInput.value : "",
        false,
      );
    });
  if (wigleClear)
    wigleClear.addEventListener("click", () => {
      if (wigleApiNameInput) wigleApiNameInput.value = "";
      if (wigleApiTokenInput) wigleApiTokenInput.value = "";
      saveWigleSettings("", "", true);
    });
  if (tailscaleInstallBtn)
    tailscaleInstallBtn.addEventListener("click", () => {
      tailscaleReauthMode = false;
      openTailscaleModal();
    });
  if (tailscaleReauthBtn)
    tailscaleReauthBtn.addEventListener("click", () => {
      tailscaleReauthMode = true;
      openTailscaleModal();
    });
  if (tailscaleModalSave)
    tailscaleModalSave.addEventListener("click", submitTailscaleInstall);
  if (tailscaleModalCancel)
    tailscaleModalCancel.addEventListener("click", closeTailscaleModal);
  if (tailscaleModalClose)
    tailscaleModalClose.addEventListener("click", closeTailscaleModal);
  if (tailscaleModal)
    tailscaleModal.addEventListener("click", (e) => {
      if (e.target === tailscaleModal) closeTailscaleModal();
    });
  if (lootPreviewClose)
    lootPreviewClose.addEventListener("click", closePreview);
  if (lootPreview)
    lootPreview.addEventListener("click", (e) => {
      if (e.target === lootPreview) closePreview();
    });
  if (nmapVizClose) nmapVizClose.addEventListener("click", closeNmapViz);
  if (nmapVizModal)
    nmapVizModal.addEventListener("click", (e) => {
      if (e.target === nmapVizModal) closeNmapViz();
    });
  if (nmapVizFilterVuln)
    nmapVizFilterVuln.addEventListener("change", renderNmapVisualization);
  if (authModalConfirm)
    authModalConfirm.addEventListener("click", () => {
      resolveAuthPrompt({
        recovery: authRecoveryMode,
        token: authModalToken ? authModalToken.value : "",
        username: authModalUsername ? authModalUsername.value : "",
        password: authModalPassword ? authModalPassword.value : "",
        confirm: authModalPasswordConfirm ? authModalPasswordConfirm.value : "",
      });
    });
  if (authModalCancel)
    authModalCancel.addEventListener("click", () => resolveAuthPrompt(null));
  if (authModalClose)
    authModalClose.addEventListener("click", () => resolveAuthPrompt(null));
  if (authModal)
    authModal.addEventListener("click", (e) => {
      if (e.target === authModal) resolveAuthPrompt(null);
    });
  if (authModalToggleRecovery)
    authModalToggleRecovery.addEventListener("click", () => {
      setRecoveryMode(!authRecoveryMode);
    });
  const authSubmitFromEnter = (e) => {
    if (e.key === "Enter") {
      e.preventDefault();
      resolveAuthPrompt({
        recovery: authRecoveryMode,
        token: authModalToken ? authModalToken.value : "",
        username: authModalUsername ? authModalUsername.value : "",
        password: authModalPassword ? authModalPassword.value : "",
        confirm: authModalPasswordConfirm ? authModalPasswordConfirm.value : "",
      });
    } else if (e.key === "Escape") {
      e.preventDefault();
      resolveAuthPrompt(null);
    }
  };
  if (authModalToken)
    authModalToken.addEventListener("keydown", authSubmitFromEnter);
  if (authModalUsername)
    authModalUsername.addEventListener("keydown", authSubmitFromEnter);
  if (authModalPassword)
    authModalPassword.addEventListener("keydown", authSubmitFromEnter);
  if (authModalPasswordConfirm)
    authModalPasswordConfirm.addEventListener("keydown", authSubmitFromEnter);
  loadAuthToken();
  setActiveTab("device");

  let payloadPollTimer = null;
  let systemPollTimer = null;

  function schedulePayloadPoll() {
    if (payloadPollTimer) clearTimeout(payloadPollTimer);
    const delay = document.hidden ? 6000 : 1500;
    payloadPollTimer = setTimeout(async () => {
      await pollPayloadStatus();
      await loadHeadlessStatus();
      if (payloadState.activePath) {
        await loadPayloadLog();
      }
      schedulePayloadPoll();
    }, delay);
  }

  function scheduleSystemPoll() {
    if (systemPollTimer) clearTimeout(systemPollTimer);
    const delay = document.hidden ? 10000 : 3000;
    systemPollTimer = setTimeout(async () => {
      if (activeTab === "device" || systemOpen) {
        await loadSystemStatus();
      }
      scheduleSystemPoll();
    }, delay);
  }

  document.addEventListener("visibilitychange", () => {
    if (!document.hidden) {
      if (activeTab === "device" || systemOpen) loadSystemStatus();
      pollPayloadStatus();
      loadHeadlessStatus();
      loadPayloadLog();
    }
    schedulePayloadPoll();
    scheduleSystemPoll();
  });

  const startAfterAuth = () => {
    ensureAuthenticated("Log in to access JackPack.").then((ok) => {
      if (!ok) {
        setTimeout(startAfterAuth, 0);
        return;
      }
      connect();
      renderPayloadActions();
      loadPayloads();
      loadSystemStatus();
      loadHeadlessStatus();
      loadNetworkStatus();
      pollPayloadStatus().then(() => loadPayloadLog()).catch(() => loadPayloadLog());
      schedulePayloadPoll();
      scheduleSystemPoll();
    });
  };
  startAfterAuth();
})();
