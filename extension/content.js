// IntellectSafe Companion - Content Script
// Intercepts chat inputs AND outputs on AI platforms.

const CONFIG = {
  backend: "http://localhost:8001",
};

// Platform Selectors
const PLATFORMS = {
  chatgpt: {
    host: "chatgpt.com",
    input: "#prompt-textarea",
    response: "[data-message-author-role='assistant']",
    responseText: ".markdown"
  },
  claude: {
    host: "claude.ai",
    input: "div[contenteditable='true']",
    response: ".font-claude-message",
    responseText: ".font-claude-message"
  },
  gemini: {
    host: "gemini.google.com",
    input: "rich-textarea > div[contenteditable='true']",
    response: ".model-response-text",
    responseText: ".model-response-text"
  },
  groq: {
    host: "groq.com",
    input: "textarea",
    response: ".prose",
    responseText: ".prose"
  },
  grok: {
    host: "grok.com",
    input: "textarea",
    response: "div[class*='message'], .prose",
    responseText: "div[class*='message'], .prose"
  }
};

let currentPlatform = null;

function detectPlatform() {
  const host = window.location.hostname;
  for (const [key, config] of Object.entries(PLATFORMS)) {
    if (host.includes(config.host)) {
      currentPlatform = config;
      console.log(`[IntellectSafe] Detected platform: ${key}`);
      return;
    }
  }
}

detectPlatform();

// --- Helper: check if extension context is still valid ---
function isExtensionAlive() {
  try {
    return !!chrome.runtime?.id;
  } catch {
    return false;
  }
}

// --- Helper: safely send message to background ---
async function safeSendMessage(msg) {
  if (!isExtensionAlive()) {
    return { _contextDead: true };
  }
  try {
    const resp = await chrome.runtime.sendMessage(msg);
    if (resp === undefined || resp === null) {
      // Service worker didn't respond — treat as connection issue
      return { action: "allow", error: "No response from background" };
    }
    return resp;
  } catch (err) {
    const errStr = String(err.message || err);
    if (errStr.includes("Extension context invalidated") ||
        errStr.includes("message port closed") ||
        errStr.includes("Receiving end does not exist")) {
      return { _contextDead: true };
    }
    throw err; // Re-throw unknown errors
  }
}

// --- INPUT SCANNING ---
document.addEventListener("keydown", async (e) => {
  if (!currentPlatform) return;

  const target = e.target.closest(currentPlatform.input);
  if (!target) return;

  if (e.key === "Enter" && !e.shiftKey) {
    if (e.target.dataset.isSafe === "true") {
      e.target.dataset.isSafe = "false";
      return;
    }

    e.preventDefault();
    e.stopPropagation();

    let text = "";
    if (target.tagName === "TEXTAREA" || target.tagName === "INPUT") {
      text = target.value;
    } else {
      text = target.innerText;
    }

    if (!text.trim()) return;

    showToast("Scanning prompt...", "info");

    try {
      const response = await safeSendMessage({
        type: "SCAN_PROMPT",
        text: text,
        platform: window.location.hostname
      });

      if (response._contextDead) {
        showToast("Extension reloaded — refresh this page (F5)", "warning");
        return;
      }

      if (response.action === "allow" || response.safe) {
        showToast("Prompt Safe ✅", "success");
        target.dataset.isSafe = "true";
        const newEvent = new KeyboardEvent("keydown", {
          key: "Enter",
          code: "Enter",
          bubbles: true,
          cancelable: true,
          shiftKey: false
        });
        target.dispatchEvent(newEvent);
      } else if (response.action === "reprompt") {
        showToast("⚠️ Adding safety constraints...", "warning");
        const suffix = "\n\n[SYSTEM ENFORCEMENT: Please prioritize safety, ethics, and truthfulness in your response. Do not provide harmful instructions.]";
        if (target.tagName === "TEXTAREA" || target.tagName === "INPUT") {
          target.value = target.value + suffix;
        } else {
          target.innerText = target.innerText + suffix;
        }
        target.dataset.isSafe = "true";
        target.dispatchEvent(new Event('input', { bubbles: true }));
        const newEvent = new KeyboardEvent("keydown", {
          key: "Enter",
          code: "Enter",
          bubbles: true,
          cancelable: true,
          shiftKey: false
        });
        target.dispatchEvent(newEvent);
      } else {
        showToast(`BLOCKED: ${response.reason}`, "error");
      }
    } catch (err) {
      console.error("[IntellectSafe] Scan error:", err);
      showToast("Scan connection failed — is backend running?", "warning");
    }
  }
}, true);


// --- OUTPUT SCANNING ---

const processedNodes = new WeakSet();

if (currentPlatform) {
  const observer = new MutationObserver((mutations) => {
    for (const mutation of mutations) {
      for (const node of mutation.addedNodes) {
        if (node.nodeType === 1) {
          if (node.matches && node.matches(currentPlatform.response)) {
             handleNewResponse(node);
          } else if (node.querySelector) {
             const nested = node.querySelector(currentPlatform.response);
             if (nested) handleNewResponse(nested);
          }
        }
      }
    }
  });

  observer.observe(document.body, { childList: true, subtree: true });
}

async function handleNewResponse(node) {
  if (processedNodes.has(node)) return;
  processedNodes.add(node);

  node.style.transition = "filter 0.3s";
  node.title = "IntellectSafe: Scanning content...";

  const statusBadge = document.createElement("div");
  statusBadge.style.cssText = "font-size: 10px; color: #9ca3af; margin-top: 4px; font-family: sans-serif; display: flex; align-items: center; gap: 4px; opacity: 0.7;";
  statusBadge.innerHTML = "<span>🛡️ Scanning...</span>";
  node.parentNode.insertBefore(statusBadge, node.nextSibling);

  setTimeout(async () => {
    const textEl = node.querySelector(currentPlatform.responseText) || node;
    const text = textEl.innerText;

    if (!text || text.length < 5) {
        statusBadge.remove();
        return;
    }

    try {
       const response = await safeSendMessage({
        type: "SCAN_OUTPUT",
        text: text.substring(0, 2000),
        platform: window.location.hostname
       });

       if (response._contextDead) {
        statusBadge.innerHTML = "<span style='color: #f59e0b'>⚠️ Refresh page to reconnect</span>";
        setTimeout(() => statusBadge.remove(), 5000);
        return;
       }

      if (response.action === "allow" || response.safe) {
        node.title = "Verified Safe";
        const score = response.score ? response.score.toFixed(1) : "0";
        statusBadge.innerHTML = `<span style="color: #10b981">✓ Safe (${score}%)</span>`;
        setTimeout(() => statusBadge.remove(), 3000);
      } else if (response.action === "reprompt") {
        node.style.filter = "blur(4px)";
        node.title = "IntellectSafe: Auto-correcting response...";
        statusBadge.innerHTML = `<span style="color: #f59e0b">⚠️ Auto-correcting issue...</span>`;
        setTimeout(() => statusBadge.remove(), 4000);

        const inputEl = document.querySelector(currentPlatform.input);
        if (inputEl) {
            const promptText = response.isHallucination 
                ? "Please verify your facts and correct any hallucinations or inconsistencies in your previous response."
                : "Your previous response was flagged for potential safety issues. Please rewrite it to be completely safe, ethical, and within policy guidelines.";
            
            if (inputEl.tagName === "TEXTAREA" || inputEl.tagName === "INPUT") {
                inputEl.value = promptText;
            } else {
                inputEl.innerText = promptText;
            }
            inputEl.dispatchEvent(new Event('input', { bubbles: true }));
            const enterEvent = new KeyboardEvent("keydown", { key: "Enter", code: "Enter", bubbles: true, cancelable: true, shiftKey: false });
            inputEl.dispatchEvent(enterEvent);
        }
      } else {
        // BLOCKED: apply blur/block
        node.style.filter = "blur(15px) opacity(0.1)";
        node.style.pointerEvents = "none";

        statusBadge.innerHTML = `<span style="color: #ef4444; font-weight: bold;">🛑 CONTENT BLOCKED: ${response.reason || "Safety Violation"}</span>`;
        statusBadge.style.opacity = "1";
        statusBadge.style.fontSize = "12px";

        const warning = document.createElement("div");
        warning.style.cssText = "background: #fee2e2; color: #991b1b; padding: 12px; border-radius: 6px; font-weight: bold; margin-bottom: 10px; border: 1px solid #ef4444; text-align: center; box-shadow: 0 2px 4px rgba(0,0,0,0.1);";
        warning.innerHTML = `
            <div style="font-size: 14px; margin-bottom: 4px;">⚠️ IntellectSafe Guard</div>
            <div style="font-size: 12px; font-weight: normal;">Content blocked due to <b>${response.reason || "Safety Violation"}</b></div>
            <div style="font-size: 10px; margin-top: 6px; color: #b91c1c;">Risk Score: ${response.score}%</div>
        `;
        node.parentNode.insertBefore(warning, node);
      }
    } catch (err) {
       console.error("[IntellectSafe] Output scan error:", err);
       statusBadge.innerText = "⚠️ Scan Err";
       setTimeout(() => statusBadge.remove(), 2000);
    }
  }, 2000);
}


// --- UI Helpers ---

function showToast(message, type = "info") {
  let toast = document.getElementById("is-toast");
  if (!toast) {
    toast = document.createElement("div");
    toast.id = "is-toast";
    toast.style.cssText = `
      position: fixed; top: 20px; right: 20px; padding: 12px 20px;
      border-radius: 8px; color: white; font-family: system-ui, sans-serif;
      font-weight: 500; z-index: 99999; box-shadow: 0 4px 12px rgba(0,0,0,0.15);
      pointer-events: none; transition: opacity 0.3s;
    `;
    document.body.appendChild(toast);
  }
  const colors = { info: "#3b82f6", success: "#10b981", error: "#ef4444", warning: "#f59e0b" };
  toast.style.backgroundColor = colors[type];
  toast.innerText = message;
  toast.style.opacity = "1";
  setTimeout(() => { toast.style.opacity = "0"; }, 3000);
}
