const tokenEl = document.getElementById("token");
const pthEl = document.getElementById("pth");
const indexEl = document.getElementById("index");
const uploadBtn = document.getElementById("upload");
const statusEl = document.getElementById("status");

uploadBtn.addEventListener("click", async () => {
  const token = tokenEl.value.trim();
  const pthFile = pthEl.files[0];
  const indexFile = indexEl.files[0];

  if (!token) {
    statusEl.textContent = "Isi kode upload dulu.";
    return;
  }
  if (!pthFile || !indexFile) {
    statusEl.textContent = "Pilih kedua file (.pth dan .index) dulu.";
    return;
  }

  const form = new FormData();
  form.append("token", token);
  form.append("pth_file", pthFile);
  form.append("index_file", indexFile);

  uploadBtn.disabled = true;
  statusEl.textContent = `Mengupload ${pthFile.name} + ${indexFile.name}... (bisa beberapa menit tergantung ukuran file)`;

  try {
    const res = await fetch("/api/upload-voice-model", {
      method: "POST",
      body: form,
    });

    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      throw new Error(err.detail || `Server error (${res.status})`);
    }

    const data = await res.json();
    statusEl.textContent = data.rvc_model_loaded
      ? "Berhasil! Suara Anda sudah aktif — coba buka halaman utama."
      : "File tersimpan, tapi model belum terbaca. Cek nama/isi file.";
  } catch (err) {
    statusEl.textContent = `Gagal: ${err.message}`;
  } finally {
    uploadBtn.disabled = false;
  }
});
