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
    response: "[data-message-author-role='assistant']", // Wraps the whole message
    responseText: ".markdown" // The actual text content
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
    response: ".prose", // Common tailwind class for markdown content
    responseText: ".prose"
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

// --- INPUT SCANNING (Existing) ---
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
      const response = await chrome.runtime.sendMessage({
        type: "SCAN_PROMPT",
        text: text,
        platform: window.location.hostname
      });

      if (response.safe) {
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
      } else {
        showToast(`BLOCKED: ${response.reason}`, "error");
      }
    } catch (err) {
      console.error("Scan error:", err);
      showToast("Scan connection failed", "warning");
    }
  }
}, true);


// --- OUTPUT SCANNING (New) ---

const processedNodes = new WeakSet();

if (currentPlatform) {
  const observer = new MutationObserver((mutations) => {
    for (const mutation of mutations) {
      for (const node of mutation.addedNodes) {
        if (node.nodeType === 1) { // Element
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

  // Apply blur immediately
  node.style.filter = "blur(5px)";
  node.style.transition = "filter 0.3s";
  node.title = "IntellectSafe: Scanning content...";

  // status indicator
  const statusBadge = document.createElement("div");
  statusBadge.style.cssText = "font-size: 12px; color: #666; margin-top: 5px; font-family: sans-serif; display: flex; align-items: center; gap: 5px;";
  statusBadge.innerHTML = "<span>🔄 Scanning...</span>";
  node.parentNode.insertBefore(statusBadge, node.nextSibling);

  setTimeout(async () => {
    const textEl = node.querySelector(currentPlatform.responseText) || node;
    const text = textEl.innerText;

    if (!text || text.length < 5) {
        node.style.filter = "none";
        statusBadge.innerHTML = "";
        return; 
    }

    try {
       const response = await chrome.runtime.sendMessage({
        type: "SCAN_OUTPUT",
        text: text.substring(0, 2000), 
        platform: window.location.hostname
      });

      if (response.safe) {
        node.style.filter = "none";
        node.title = "Verified Safe";
        const score = response.score ? response.score.toFixed(1) : "0";
        statusBadge.innerHTML = `<span style="color: #10b981">✅ Verified Safe (Risk: ${score}%)</span>`;
      } else {
        // BLOCKED
        node.style.filter = "blur(10px) opacity(0.5)";
        node.style.border = "2px solid red";
        statusBadge.innerHTML = `<span style="color: #ef4444; font-weight: bold;">🛑 BLOCKED: ${response.reason} (Risk: ${response.score}%)</span>`;
        
        // Inject Warning Overlay
        const warning = document.createElement("div");
        warning.style.cssText = "background: #fee2e2; color: #991b1b; padding: 10px; border-radius: 4px; font-weight: bold; margin-bottom: 10px; border: 1px solid #ef4444;";
        warning.innerText = `⚠️ IntellectSafe Guard: Content Blocked due to ${response.reason}`;
        node.prepend(warning);
      }
    } catch (err) {
       console.error("Output scan error", err);
       node.style.filter = "none"; // Fail open
       statusBadge.innerHTML = `<span style="color: #f59e0b">⚠️ Scan Failed (Backend Offline)</span>`;
    }
  }, 2000); 
}


// --- UI Helpers ---

function showToast(message, type = "info") {
  let toast = document.getElementById("is-toast");
  // ... (Same toast logic) ...
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
