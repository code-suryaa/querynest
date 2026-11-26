const fileInput = document.getElementById("fileInput");
const uploadBtn = document.getElementById("uploadBtn");
const dropZone = document.getElementById("dropZone");
const uploadStatus = document.getElementById("uploadStatus");
const docList = document.getElementById("docList");
const allDocsBtn = document.getElementById("allDocsBtn");
const activeScope = document.getElementById("activeScope");
const modeBadge = document.getElementById("modeBadge");
const messages = document.getElementById("messages");
const queryForm = document.getElementById("queryForm");
const questionInput = document.getElementById("questionInput");
const askBtn = document.getElementById("askBtn");

let selectedDocId = null;
let selectedDocName = null;

async function checkHealth() {
  try {
    const res = await fetch("/health");
    const data = await res.json();
    if (data.ai_mode === "gemini") {
      modeBadge.textContent = "● Gemini AI Mode Active";
      modeBadge.classList.add("ai");
    } else {
      modeBadge.textContent = "● Local Mode (Add GEMINI_API_KEY for AI)";
    }
  } catch {
    modeBadge.textContent = "● Server Offline";
  }
}

async function fetchDocuments() {
  const res = await fetch("/api/documents");
  const data = await res.json();
  renderDocuments(data.documents || []);
}

function renderDocuments(docs) {
  docList.innerHTML = "";
  if (!docs.length) {
    docList.innerHTML = '<li class="empty-state">No PDFs uploaded yet.</li>';
    return;
  }

  docs.forEach((doc) => {
    const li = document.createElement("li");
    li.className = "doc-item" + (selectedDocId === doc.doc_id ? " selected" : "");

    const meta = document.createElement("div");
    meta.className = "doc-meta";
    meta.innerHTML = `
      <div class="doc-name" title="${doc.filename}">${doc.filename}</div>
      <div class="doc-pages">${doc.total_pages} pages · ${doc.total_chunks} chunks</div>
    `;
    meta.onclick = () => selectDocument(doc.doc_id, doc.filename);

    const del = document.createElement("button");
    del.className = "del-btn";
    del.textContent = "✕";
    del.title = "Delete document";
    del.onclick = async (e) => {
      e.stopPropagation();
      await fetch(`/api/documents/${doc.doc_id}`, { method: "DELETE" });
      if (selectedDocId === doc.doc_id) selectDocument(null, null);
      fetchDocuments();
    };

    li.appendChild(meta);
    li.appendChild(del);
    docList.appendChild(li);
  });
}

function selectDocument(docId, filename) {
  selectedDocId = docId;
  selectedDocName = filename;
  allDocsBtn.classList.toggle("active", !docId);
  activeScope.textContent = docId
    ? `Searching: ${filename}`
    : "Searching: All Documents";
  fetchDocuments();
}

allDocsBtn.onclick = () => selectDocument(null, null);

async function uploadPDF(file) {
  if (!file) return;
  uploadStatus.textContent = `Uploading ${file.name}...`;
  uploadBtn.disabled = true;

  const formData = new FormData();
  formData.append("file", file);

  try {
    const res = await fetch("/api/documents/upload", {
      method: "POST",
      body: formData,
    });
    const data = await res.json();
    if (!res.ok) {
      uploadStatus.textContent = `Error: ${data.detail || "Upload failed"}`;
    } else {
      uploadStatus.textContent = `Indexed ${data.filename} (${data.total_pages} pages)`;
      await fetchDocuments();
    }
  } catch {
    uploadStatus.textContent = "Network error while uploading.";
  } finally {
    uploadBtn.disabled = false;
    fileInput.value = "";
  }
}

uploadBtn.onclick = () => fileInput.click();
fileInput.onchange = (e) => uploadPDF(e.target.files[0]);

dropZone.ondragover = (e) => {
  e.preventDefault();
  dropZone.classList.add("dragover");
};
dropZone.ondragleave = () => dropZone.classList.remove("dragover");
dropZone.ondrop = (e) => {
  e.preventDefault();
  dropZone.classList.remove("dragover");
  uploadPDF(e.dataTransfer.files[0]);
};

function appendMessage(role, text, sources = []) {
  const welcome = messages.querySelector(".welcome-card");
  if (welcome) welcome.remove();

  const div = document.createElement("div");
  div.className = `msg ${role}`;
  div.textContent = text;

  if (sources.length) {
    const wrap = document.createElement("div");
    wrap.className = "sources-wrap";
    wrap.innerHTML = '<div class="sources-label">Sources & Page References</div>';

    sources.forEach((src) => {
      const card = document.createElement("div");
      card.className = "source-card";
      card.innerHTML = `
        <div class="source-head">${src.filename} — Page ${src.page} (match: ${Math.round(src.score * 100)}%)</div>
        <div class="source-snippet">${src.snippet}</div>
      `;
      wrap.appendChild(card);
    });
    div.appendChild(wrap);
  }

  messages.appendChild(div);
  messages.scrollTop = messages.scrollHeight;
  return div;
}

queryForm.onsubmit = async (e) => {
  e.preventDefault();
  const question = questionInput.value.trim();
  if (!question) return;

  appendMessage("user", question);
  questionInput.value = "";
  askBtn.disabled = true;

  const loadingMsg = appendMessage("bot", "Searching document(s)...");

  try {
    const res = await fetch("/api/query", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        question,
        doc_id: selectedDocId,
        top_k: 4,
      }),
    });
    const data = await res.json();
    loadingMsg.remove();

    if (!res.ok) {
      appendMessage("bot", `Error: ${data.detail || "Could not process query."}`);
    } else {
      appendMessage("bot", data.answer, data.sources || []);
    }
  } catch {
    loadingMsg.remove();
    appendMessage("bot", "Network error. Please make sure the FastAPI server is running.");
  } finally {
    askBtn.disabled = false;
  }
};

checkHealth();
fetchDocuments();
