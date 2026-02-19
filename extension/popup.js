document.addEventListener('DOMContentLoaded', () => {
    // Load saved URL
    chrome.storage.local.get(['backendUrl'], (result) => {
        if (result.backendUrl) {
            document.getElementById('backend-url').value = result.backendUrl;
        }
    });

    document.getElementById("open-dashboard").addEventListener("click", () => {
        chrome.tabs.create({ url: "http://localhost:5173" });
    });

    document.getElementById('save-url').addEventListener('click', () => {
        let url = document.getElementById('backend-url').value.trim();
        if (!url) return;
        
        // Remove trailing slash
        url = url.replace(/\/$/, "");

        chrome.storage.local.set({ backendUrl: url }, () => {
            const msg = document.getElementById('save-msg');
            msg.innerText = "Saved!";
            
            // Notify background
            chrome.runtime.sendMessage({ type: "CONFIG_UPDATED", url: url });
            
            setTimeout(() => { msg.innerText = ""; }, 2000);
        });
    });
});
