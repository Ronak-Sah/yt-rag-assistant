document.addEventListener("DOMContentLoaded", () => {

    const askBtn = document.getElementById("askBtn");  // <-- matches popup.html
    const responseBox = document.getElementById("response");
    const questionInput = document.getElementById("question");

    askBtn.addEventListener("click", async () => {

        let question = questionInput.value.trim();

        if (!question) {
            responseBox.innerHTML = "⚠ Please enter a question!";
            return;
        }

        // Get current YouTube video URL
        chrome.tabs.query({ active: true, currentWindow: true }, async (tabs) => {

            let video_url = tabs[0].url;
            console.log(video_url)
            if (!video_url.includes("youtube.com") && !video_url.includes("youtu.be")) {
                responseBox.innerHTML = "❌ This is not a YouTube video!";
                return;
            }

            responseBox.innerHTML = "⏳ Processing video transcript...";

            try {
                let res = await fetch("http://127.0.0.1:5000/ask_video", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({
                        url: video_url,
                        question: question
                    })
                });

                const data = await res.json();

                if (data.answer) {
                    responseBox.innerHTML = "💡 " + data.answer;
                } else {
                    responseBox.innerHTML = "❌ No response from backend";
                }
            }

            catch (err) {
                console.log("API error:", err);
                responseBox.innerHTML = "❌ API not reachable — Start backend";
            }
        })
    });

});
