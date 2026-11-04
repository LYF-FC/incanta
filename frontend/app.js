let gaugesVisible = true;
let lastGaugeValues = {};

function toggleGauges() {
  gaugesVisible = !gaugesVisible;
  document.getElementById("gauge-container").style.display = gaugesVisible ? "block" : "none";
  document.getElementById("toggle-gauges").innerText = gaugesVisible ? "Hide Gauges" : "Show Gauges";
}

document.getElementById("chat-form").addEventListener("submit", async (e) => {
  e.preventDefault();

  const input = document.getElementById("chat-input");
  const message = input.value.trim();
  if (message === "") return;

  appendMessage("user", message);
  input.value = "";

  try {
    const response = await fetch("/api/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message }),
    });

    const data = await response.json();
    appendMessage("celeste", data.response);
    updateEmotion(data.emotion);
    updateGauges(data.gauges);
  } catch (error) {
    console.error("Error communicating with backend:", error);
  }
});

function appendMessage(sender, message) {
  const chat = document.getElementById("chat-messages");
  const bubble = document.createElement("div");
  bubble.classList.add("chat-bubble", sender);
  bubble.innerHTML = `<span>${message}</span>`;
  chat.appendChild(bubble);
  chat.scrollTop = chat.scrollHeight;
}

function updateEmotion(emotion) {
  const e = document.getElementById("emotion-label");
  e.innerText = `Current Emotion: ${emotion}`;
}

function updateGauges(newGauges) {
  for (const [name, value] of Object.entries(newGauges)) {
    const gaugeBar = document.getElementById(`gauge-${name}`);
    if (!gaugeBar) continue;

    const oldVal = lastGaugeValues[name] ?? 0;
    gaugeBar.style.width = `${value}%`;
    gaugeBar.innerText = `${name}: ${value}`;

    const gaugeFill = gaugeBar.parentElement;
    gaugeFill.classList.remove("gain", "loss");
    void gaugeFill.offsetWidth; // Force reflow to reset animation

    if (value > oldVal) gaugeFill.classList.add("gain");
    else if (value < oldVal) gaugeFill.classList.add("loss");

    lastGaugeValues[name] = value;
  }
}

// Initial call to load baseline
window.onload = async () => {
  try {
    const res = await fetch("/api/status");
    const data = await res.json();
    updateEmotion(data.emotion);
    updateGauges(data.gauges);
  } catch (err) {
    console.error("Failed to fetch initial status:", err);
  }
};