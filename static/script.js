<script>

// REST helper
async function api(path, method = "GET", body = null) {
    const opts = { method, headers: {} };
    if (body) {
        opts.headers["Content-Type"] = "application/json";
        opts.body = JSON.stringify(body);
    }
    const res = await fetch(path, opts);
    return res.json();
}

// Update queue UI based on websocket snapshot
-
function updateUI(state) {
    const queueList = document.querySelector(".queue-list");
    queueList.innerHTML = ""; // clear existing

    // state.queue is list of {mac, name}
    state.queue.forEach(dev => {
        const div = document.createElement("div");
        div.className = "queue-item";

        div.innerHTML = `
            <div class="device-name">Device Name: 
                <span style="color:#9ecbff;">${dev.name}</span>
            </div>
            <div class="mac">MAC: ${dev.mac}</div>
        `;

        queueList.appendChild(div);
    });


}


// WebSocket connection (live updates)

function startWebSocket() {
    const ws = new WebSocket("ws://" + window.location.hostname + ":8765");

    ws.onmessage = (msg) => {
        const state = JSON.parse(msg.data);
        updateUI(state);
    };

    ws.onclose = () => {
        console.warn("WS disconnected — retrying...");
        setTimeout(startWebSocket, 2000);
    };
}


// Button event listeners

async function handleSkip() {
    await api("/skip", "POST");
}

async function handleStop() {
    await api("/endTurn", "POST");
}

document.addEventListener("DOMContentLoaded", () => {
    document.querySelector(".skip-btn")
        .addEventListener("click", handleSkip);

    document.querySelector(".stop-btn")
        .addEventListener("click", handleStop);

    startWebSocket();
});
</script>
