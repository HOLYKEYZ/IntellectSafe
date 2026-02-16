document.getElementById("open-dashboard").addEventListener("click", () => {
  chrome.tabs.create({ url: "http://localhost:5173" });
});
