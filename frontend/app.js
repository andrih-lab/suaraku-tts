const textEl = document.getElementById("text");
const charcountEl = document.getElementById("charcount");
const languageEl = document.getElementById("language");
const cloneVoiceEl = document.getElementById("cloneVoice");
const generateBtn = document.getElementById("generate");
const statusEl = document.getElementById("status");
const playerEl = document.getElementById("player");
const downloadEl = document.getElementById("download");

textEl.addEventListener("input", () => {
  charcountEl.textContent = textEl.value.length;
});

generateBtn.addEventListener("click", async () => {
  const text = textEl.value.trim();
  if (!text) {
    statusEl.textContent = "Tulis teks dulu.";
    return;
  }

  generateBtn.disabled = true;
  statusEl.textContent = "Membuat suara...";
  playerEl.style.display = "none";
  downloadEl.style.display = "none";

  try {
    const res = await fetch("/api/tts", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        text,
        language: languageEl.value,
        clone_voice: cloneVoiceEl.checked,
      }),
    });

    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      throw new Error(err.detail || `Server error (${res.status})`);
    }

    const blob = await res.blob();
    const url = URL.createObjectURL(blob);

    playerEl.src = url;
    playerEl.style.display = "block";
    playerEl.play();

    downloadEl.href = url;
    downloadEl.style.display = "block";

    statusEl.textContent = "Selesai.";
  } catch (err) {
    statusEl.textContent = `Gagal: ${err.message}`;
  } finally {
    generateBtn.disabled = false;
  }
});
