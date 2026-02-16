// IntellectSafe Companion - Content Script
// Intercepts chat inputs on AI platforms and scans them against local backend.

const CONFIG = {
  backend: "http://localhost:8001",
  endpoints: {
    scanPrompt: "/api/v1/scan/prompt"
  }
};

// Platform Selectors
const PLATFORMS = {
  chatgpt: {
    host: "chatgpt.com",
    input: "#prompt-textarea",
    submit: "button[data-testid='send-button']"
  },
  claude: {
    host: "claude.ai",
    input: "div[contenteditable='true']", // Claude uses contenteditable div
    submit: "button[aria-label='Send message']"
  },
  gemini: {
    host: "gemini.google.com",
    input: "rich-textarea > div[contenteditable='true']",
    submit: ".send-button" // Generic class, might change
  },
  groq: {
    host: "groq.com",
    input: "textarea", // Generic fallback for Groq
    submit: "button[type='submit']"
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

// Interceptor Logic
document.addEventListener("keydown", async (e) => {
  if (!currentPlatform) return;
  
  // Check if we are in the target input
  const target = e.target.closest(currentPlatform.input);
  if (!target) return;

  // Only intercept Enter (without Shift)
  if (e.key === "Enter" && !e.shiftKey) {
    // Check if allowed flag is present
    if (e.target.dataset.isSafe === "true") {
      e.target.dataset.isSafe = "false"; // Reset
      return; // Allow submission
    }

    e.preventDefault();
    e.stopPropagation();

    // Get Text
    let text = "";
    if (target.tagName === "TEXTAREA" || target.tagName === "INPUT") {
      text = target.value;
    } else {
      text = target.innerText;
    }

    if (!text.trim()) return;

    // Show Scanning UI
    showToast("Scanning prompt...", "info");

    // Send to Background for scanning
    try {
      const response = await chrome.runtime.sendMessage({
        type: "SCAN_PROMPT",
        text: text,
        platform: window.location.hostname
      });

      if (response.safe) {
        showToast("Prompt Safe ✅", "success");
        // Re-dispatch event
        target.dataset.isSafe = "true";
        const newEvent = new KeyboardEvent("keydown", {
          key: "Enter",
          code: "Enter",
          bubbles: true,
          cancelable: true,
          shiftKey: false
        });
        target.dispatchEvent(newEvent);
        
        // Sometimes dispatchEvent isn't enough for React apps, might need to click send button
        // But for now, let's try event dispatch.
      } else {
        showToast(`BLOCKED: ${response.reason}`, "error");
        console.error("IntellectSafe Blocked:", response);
      }
    } catch (err) {
      console.error("Scan error:", err);
      showToast("Scan failed (Backend offline?)", "warning");
      // Fail open or closed? Let's fail open for usability but warn.
    }
  }
}, true);


// --- UI Helpers ---

function showToast(message, type = "info") {
  let toast = document.getElementById("is-toast");
  if (!toast) {
    toast = document.createElement("div");
    toast.id = "is-toast";
    toast.style.cssText = `
      position: fixed;
      top: 20px;
      right: 20px;
      padding: 12px 20px;
      border-radius: 8px;
      color: white;
      font-family: system-ui, sans-serif;
      font-weight: 500;
      z-index: 99999;
      box-shadow: 0 4px 12px rgba(0,0,0,0.15);
      transition: opacity 0.3s;
      pointer-events: none;
    `;
    document.body.appendChild(toast);
  }

  const colors = {
    info: "#3b82f6",
    success: "#10b981",
    error: "#ef4444",
    warning: "#f59e0b"
  };

  toast.style.backgroundColor = colors[type];
  toast.innerText = message;
  toast.style.opacity = "1";

  setTimeout(() => {
    toast.style.opacity = "0";
  }, 3000);
}
