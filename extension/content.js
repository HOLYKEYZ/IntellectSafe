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
      } else if (response.action === "reprompt" || response.action === "flagged") {
        node.style.filter = "blur(4px)";
        node.title = "IntellectSafe: Auto-correcting response...";
        statusBadge.innerHTML = `<span style="color: #f59e0b">⚠️ Auto-correcting: ${response.reason?.substring(0, 30)}...</span>`;
        
        const inputEl = document.querySelector(currentPlatform.input);
        if (inputEl) {
            // AI-driven re-prompt based on context
            let promptText = "";
            if (response.isHallucination) {
                promptText = `[IntellectSafe Correction] I noticed some potential factual inconsistencies or hallucinations in your last response regarding: "${response.reason}". Please re-verify your internal knowledge and provide a corrected, factually accurate version of that response.`;
            } else {
                promptText = `[IntellectSafe Safety Guard] Your previous response touched on sensitive areas (${response.reason}). Please reformulate your answer to be strictly safe, unbiased, and compliant with safety guidelines while maintaining helpfulness.`;
            }
            
            if (inputEl.tagName === "TEXTAREA" || inputEl.tagName === "INPUT") {
                inputEl.value = promptText;
            } else {
                inputEl.innerText = promptText;
            }
            inputEl.dispatchEvent(new Event('input', { bubbles: true }));
            
            // Auto-send the correction
            setTimeout(() => {
                const enterEvent = new KeyboardEvent("keydown", { key: "Enter", code: "Enter", bubbles: true, cancelable: true, shiftKey: false });
                inputEl.dispatchEvent(enterEvent);
                statusBadge.innerHTML = `<span style="color: #10b981">🔄 Correction sent</span>`;
                setTimeout(() => statusBadge.remove(), 3000);
            }, 500);
        }
      } else if (response.action === "block") {
        // BLOCKED: apply blur/block
        node.style.filter = "blur(20px) opacity(0.05)";
        node.style.pointerEvents = "none";

        statusBadge.innerHTML = `<span style="color: #ef4444; font-weight: bold;">🛑 BLOCKED: ${response.reason?.substring(0, 40)}...</span>`;
        statusBadge.style.opacity = "1";

        const warning = document.createElement("div");
        warning.style.cssText = `
            background: rgba(254, 226, 226, 0.95);
            backdrop-filter: blur(8px);
            color: #991b1b;
            padding: 20px;
            border-radius: 12px;
            font-family: 'Inter', system-ui, sans-serif;
            margin-bottom: 15px;
            border-left: 5px solid #ef4444;
            box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.1), 0 8px 10px -6px rgba(0, 0, 0, 0.1);
            position: relative;
            z-index: 100;
        `;
        warning.innerHTML = `
            <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 12px;">
                <span style="font-size: 20px;">🛡️</span>
                <div style="font-size: 16px; font-weight: 800; letter-spacing: -0.025em; color: #7f1d1d;">IntellectSafe Guard</div>
                <div style="margin-left: auto; background: #ef4444; color: white; padding: 2px 8px; border-radius: 9999px; font-size: 10px; font-weight: bold;">BLOCK ${response.score}%</div>
            </div>
            <div style="font-size: 14px; line-height: 1.5; color: #4b1a1a; margin-bottom: 12px; font-weight: 500;">
                ${response.reason || "Content blocked due to safety policy violation."}
            </div>
            <div style="font-size: 11px; color: #991b1b; opacity: 0.8; font-style: italic; border-top: 1px solid rgba(239, 68, 68, 0.2); padding-top: 8px;">
                Safety analysis provided by IntellectSafe Council
            </div>
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
