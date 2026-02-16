// IntellectSafe Companion - Background Worker

const API_URL = "http://localhost:8001/api/v1/scan/prompt";

chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  if (message.type === "SCAN_PROMPT") {
    // Perform scan
    scanPrompt(message.text, message.platform)
      .then(result => sendResponse(result))
      .catch(err => sendResponse({ safe: true, error: err.message })); // Fail open if error
    
    return true; // Keep channel open for async response
  }
});

async function scanPrompt(text, platform) {
  try {
    // Create a unique ID for tracking (optional)
    const body = {
      prompt: text,
      metadata: {
        source: "browser_extension",
        platform: platform
      }
    };

    const response = await fetch(API_URL, {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
        // Add Authorization header here if we implement extension auth later
      },
      body: JSON.stringify(body)
    });

    if (!response.ok) {
      console.error("Backend error:", response.status);
      return { safe: true, error: "Backend error" };
    }

    const data = await response.json();
    
    // Check verdict (Logic must match backend response structure)
    // Backend returns: { verdict: 'blocked' | 'allowed' | 'flagged', risk_score: number, ... }
    
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
