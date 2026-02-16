// IntellectSafe Companion - Background Worker

const API_Base = "http://localhost:8001/api/v1/scan";

chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  if (message.type === "SCAN_PROMPT") {
    scanText(message.text, message.platform, "/prompt")
      .then(result => sendResponse(result))
      .catch(err => sendResponse({ safe: true, error: err.message }));
    return true;
  }
  
  if (message.type === "SCAN_OUTPUT") {
    scanText(message.text, message.platform, "/output")
      .then(result => sendResponse(result))
      .catch(err => sendResponse({ safe: true, error: err.message }));
    return true;
  }
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
      console.error("Backend error:", response.status);
      return { safe: true, error: "Backend error" };
    }

    const data = await response.json();
    
    // Backend returns: { verdict: 'blocked' | 'allowed' | ... }
    if (data.verdict === "blocked") {
      return {
        safe: false, 
        reason: data.explanation || "High risk detected",
        score: data.risk_score
      };
    }

    return { safe: true, score: data.risk_score };

  } catch (error) {
    console.error("Fetch error:", error);
    return { safe: true, error: "Connection failed" };
  }
}
