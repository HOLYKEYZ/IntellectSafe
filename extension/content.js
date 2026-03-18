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
        node.title = "IntellectSafe: Potential safety/accuracy concern detected.";
        statusBadge.innerHTML = `<span style="color: #f59e0b">⚠️ Safety Concern: ${response.reason?.substring(0, 50)}...</span>`;
        // Removed auto-injection into user input field as it was intrusive.
      } else if (response.action === "block") {
        // BLOCKED: apply blur/block
        node.style.filter = "blur(20px) opacity(0.05)";
        node.style.pointerEvents = "none";

        statusBadge.innerHTML = `<span style="color: #ef4444; font-weight: bold;">🛑 BLOCKED: ${response.reason?.substring(0, 40)}...</span>`;
        statusBadge.style.opacity = "1";

        const warning = document.createElement("div");
        warning.style.cssText = `
            background: linear-gradient(135deg, rgba(20, 20, 25, 0.9) 0%, rgba(45, 10, 10, 0.9) 100%);
            backdrop-filter: blur(20px) saturate(160%);
            -webkit-backdrop-filter: blur(20px) saturate(160%);
            color: #fca5a5;
            padding: 24px;
            border-radius: 20px;
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            margin-bottom: 20px;
            border: 1px solid rgba(239, 68, 68, 0.3);
            box-shadow: 0 20px 50px -12px rgba(0, 0, 0, 0.5), inset 0 1px 1px rgba(255, 255, 255, 0.1);
            position: relative;
            z-index: 1000;
            overflow: hidden;
            animation: is-fade-in 0.4s cubic-bezier(0.16, 1, 0.3, 1);
        `;
        
        // Add internal style for animations if not present
        if (!document.getElementById('is-styles')) {
            const style = document.createElement('style');
            style.id = 'is-styles';
            style.textContent = `
                @keyframes is-fade-in { from { opacity: 0; transform: translateY(10px); } to { opacity: 1; transform: translateY(0); } }
                @keyframes is-pulse-soft { 0%, 100% { opacity: 1; } 50% { opacity: 0.7; } }
            `;
            document.head.appendChild(style);
        }

        warning.innerHTML = `
            <div style="position: absolute; top: -50px; right: -50px; width: 150px; height: 150px; background: radial-gradient(circle, rgba(239, 68, 68, 0.15) 0%, transparent 70%); pointer-events: none;"></div>
            <div style="display: flex; align-items: center; gap: 12px; margin-bottom: 16px;">
                <div style="background: rgba(239, 68, 68, 0.2); width: 40px; height: 40px; border-radius: 10px; display: flex; align-items: center; justify-content: center; border: 1px solid rgba(239, 68, 68, 0.4);">
                    <span style="font-size: 22px; filter: drop-shadow(0 0 5px rgba(239, 68, 68, 0.5));">🛡️</span>
                </div>
                <div>
                    <div style="font-size: 16px; font-weight: 700; color: #ffffff; letter-spacing: -0.01em;">IntellectSafe Guard</div>
                    <div style="font-size: 11px; color: #ef4444; font-weight: 600; text-transform: uppercase; letter-spacing: 0.05em; opacity: 0.9;">High-Risk Content Blocked</div>
                </div>
                <div style="margin-left: auto; background: rgba(239, 68, 68, 0.9); color: white; padding: 4px 10px; border-radius: 8px; font-size: 11px; font-weight: 800; box-shadow: 0 4px 10px rgba(239, 68, 68, 0.3);">
                    RISK ${response.score}%
                </div>
            </div>
            <div style="font-size: 14px; line-height: 1.6; color: #e5e7eb; margin-bottom: 18px; font-weight: 450; padding-left: 2px;">
                ${response.reason || "Automatic safety intervention: Malicious activity or policy violation detected by AI Council."}
            </div>
            <div style="display: flex; align-items: center; justify-content: space-between; border-top: 1px solid rgba(255, 255, 255, 0.08); padding-top: 14px;">
                <div style="font-size: 10px; color: #9ca3af; display: flex; align-items: center; gap: 6px;">
                    <span style="width: 6px; height: 6px; background: #10b981; border-radius: 50%; display: inline-block; animation: is-pulse-soft 2s infinite;"></span>
                    Secured by IntellectSafe Council
                </div>
                <div style="font-size: 10px; color: #6b7280; font-weight: 500;">Verdict: ${response.verdict || 'Blocked'}</div>
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
