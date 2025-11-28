
// PiTunes JavaScript
async function api(path, method = "GET", body = null) {
    const opts = { method, headers: {} };
    if (body) {
        opts.headers["Content-Type"] = "application/json";
        opts.body = JSON.stringify(body);
    }
    const res = await fetch(path, opts);
    return res.json();
}

// UI Update
function updateUI(state) {
    const currentEl = document.getElementById("currentDevice");
    const queueEl = document.getElementById("queue");
    const votesEl = document.getElementById("votes");

    // current user
    if (state.current) {
        currentEl.textContent = `${state.current.name} (${state.current.mac})`;
    } else {
        currentEl.textContent = "None";
    }

    // queue
    queueEl.innerHTML = "";
    state.queue.forEach(dev => {
        const li = document.createElement("li");
        li.textContent = `${dev.name} (${dev.mac})`;
        queueEl.appendChild(li);
    });

    // votes
    votesEl.textContent = `${state.votes}/${state.skip_threshold}`;
}

// WebSocket live updates 

function startWebSocket() {
    const ws = new WebSocket("ws://" + window.location.hostname + ":8765");

    ws.onmessage = (msg) => {
        const state = JSON.parse(msg.data);
        updateUI(state);
    };

    ws.onclose = () => {
        console.warn("WebSocket closed. Retrying in 2s...");
        setTimeout(startWebSocket, 2000);
    };
}

// REST endpoints

async function voteSkip() {
    await api("/skip", "POST");
}

async function endTurn() {
    await api("/endTurn", "POST");
}

// Event Listeners
window.addEventListener("DOMContentLoaded", () => {
    document.getElementById("skipBtn")
        .addEventListener("click", voteSkip);

    document.getElementById("endTurnBtn")
        .addEventListener("click", endTurn);

    startWebSocket(); 
});
