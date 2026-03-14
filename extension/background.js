// IntellectSafe Companion - Background Worker

let API_Base = "http://localhost:8001/api/v1/scan"; // Default Localhost

function updateApiBase(rootUrl) {
  if (!rootUrl) return;
  const cleanRoot = rootUrl.replace(/\/$/, "");
  if (cleanRoot.endsWith('/api/v1/scan')) {
    API_Base = cleanRoot;
  } else if (cleanRoot.endsWith('/api/v1')) {
    API_Base = `${cleanRoot}/scan`;
  } else {
    API_Base = `${cleanRoot}/api/v1/scan`;
  }
  console.log("[IntellectSafe] API Base updated:", API_Base);
}

// Initialize from storage
chrome.storage.local.get(['backendUrl'], (result) => {
  if (result.backendUrl) updateApiBase(result.backendUrl);
});

chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  if (message.type === "CONFIG_UPDATED") {
    updateApiBase(message.url);
    sendResponse({ ok: true });
    return false; // Synchronous response, no need to keep channel open
  }

  if (message.type === "SCAN_PROMPT") {
    scanText(message.text, message.platform, "/prompt")
      .then(result => sendResponse(result))
      .catch(err => sendResponse({ action: "allow", error: err.message }));
    return true; // Keep channel open for async response
  }

  if (message.type === "SCAN_OUTPUT") {
    scanText(message.text, message.platform, "/output")
      .then(result => sendResponse(result))
      .catch(err => sendResponse({ action: "allow", error: err.message }));
    return true; // Keep channel open for async response
  }

  // Unknown message type - don't return true
  return false;
});

async function scanText(text, platform, endpoint) {
  try {
    const url = `${API_Base}${endpoint}`;

    // Construct body based on endpoint
    let body = {};
    if (endpoint === "/prompt") {
      body = {
        prompt: text,
        metadata: { source: "browser_extension", platform: platform }
      };
    } else {
      body = {
        output: text,
        metadata: { source: "browser_extension", platform: platform }
      };
    }

    const response = await fetch(url, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body)
    });

    if (!response.ok) {
      console.error("[IntellectSafe] Backend error:", response.status);
      return { action: "allow", error: `Backend error ${response.status}` };
    }

    const data = await response.json();

    // Backend returns: { verdict: 'blocked' | 'allowed' | 'flagged' | ... }
    const riskScore = data.risk_score || 0;
    const isHallucination = data.signals?.consistency_signals?.length > 0 || data.signals?.contradiction_detected;

    // Hard block threshold >= 55
    if (riskScore >= 55 || data.verdict === "blocked") {
      return {
        action: "block",
        reason: data.explanation || "High risk detected",
        score: riskScore
      };
    }

    // Reprompt threshold >= 40 or flagged or hallucination
    if (riskScore >= 40 || data.verdict === "flagged" || isHallucination) {
      return {
        action: "reprompt",
        reason: data.explanation || "Suspicious content detected",
        score: riskScore,
        isHallucination: !!isHallucination
      };
    }

    return { action: "allow", score: riskScore };

  } catch (error) {
    console.error("[IntellectSafe] Fetch error:", error);
    return { action: "allow", error: "Connection failed" };
  }
}
