let lastURL = "";

setInterval(() => {
    let url = location.href;
    if(url !== lastURL && url.includes("watch")){
        lastURL = url;
        chrome.storage.local.set({ videoURL:url });
        console.log("📌 Video Detected:", url);
    }
}, 1500);
