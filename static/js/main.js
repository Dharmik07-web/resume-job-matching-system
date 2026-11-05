/**
 * SkillSync AI - Interactive Frontend Logic
 * Developed by DHARMIK MTH
 */

document.addEventListener("DOMContentLoaded", () => {
  initDropzone();
  initPresetButtons();
  initTabSwitching();
  initFormValidation();
  initExportHelpers();
});

/**
 * Drag and Drop File Upload
 */
function initDropzone() {
  const dropzone = document.getElementById("dropzone");
  const fileInput = document.getElementById("resume_file");
  const filePreview = document.getElementById("file-preview");
  const fileNameDisplay = document.getElementById("file-name-display");
  const fileSizeDisplay = document.getElementById("file-size-display");
  const removeFileBtn = document.getElementById("remove-file-btn");

  if (!dropzone || !fileInput) return;

  ["dragenter", "dragover"].forEach((eventName) => {
    dropzone.addEventListener(eventName, (e) => {
      e.preventDefault();
      e.stopPropagation();
      dropzone.classList.add("dragover");
    });
  });

  ["dragleave", "drop"].forEach((eventName) => {
    dropzone.addEventListener(eventName, (e) => {
      e.preventDefault();
      e.stopPropagation();
      dropzone.classList.remove("dragover");
    });
  });

  dropzone.addEventListener("drop", (e) => {
    const files = e.dataTransfer.files;
    if (files.length > 0) {
      handleSelectedFile(files[0]);
    }
  });

  dropzone.addEventListener("click", () => {
    fileInput.click();
  });

  fileInput.addEventListener("change", () => {
    if (fileInput.files.length > 0) {
      handleSelectedFile(fileInput.files[0]);
    }
  });

  if (removeFileBtn) {
    removeFileBtn.addEventListener("click", (e) => {
      e.stopPropagation();
      fileInput.value = "";
      if (filePreview) filePreview.classList.add("hidden");
      const dropzonePlaceholder = document.getElementById("dropzone-placeholder");
      if (dropzonePlaceholder) dropzonePlaceholder.classList.remove("hidden");
    });
  }

  function handleSelectedFile(file) {
    const allowed = ["pdf", "txt"];
    const ext = file.name.split(".").pop().toLowerCase();

    if (!allowed.includes(ext)) {
      alert("Please select a PDF or TXT file.");
      return;
    }

    if (file.size > 16 * 1024 * 1024) {
      alert("File is too large. Maximum allowed size is 16MB.");
      return;
    }

    if (fileNameDisplay) fileNameDisplay.textContent = file.name;
    if (fileSizeDisplay) {
      const sizeMb = (file.size / (1024 * 1024)).toFixed(2);
      fileSizeDisplay.textContent = `${sizeMb} MB (${ext.toUpperCase()})`;
    }

    const dropzonePlaceholder = document.getElementById("dropzone-placeholder");
    if (dropzonePlaceholder) dropzonePlaceholder.classList.add("hidden");
    if (filePreview) filePreview.classList.remove("hidden");
  }
}

/**
 * 1-Click Preset Loaders
 */
function initPresetButtons() {
  const presetButtons = document.querySelectorAll("[data-preset]");
  const resumeTextArea = document.getElementById("resume_text");
  const jdTextArea = document.getElementById("job_description");

  presetButtons.forEach((btn) => {
    btn.addEventListener("click", async () => {
      const presetKey = btn.getAttribute("data-preset");
      try {
        btn.classList.add("opacity-50", "pointer-events-none");
        const resp = await fetch(`/sample/${presetKey}`);
        const data = await resp.json();

        if (data.resume && resumeTextArea) {
          resumeTextArea.value = data.resume;
          // Switch to paste tab automatically
          const textTabBtn = document.getElementById("tab-btn-text");
          if (textTabBtn) textTabBtn.click();
        }

        if (data.jd && jdTextArea) {
          jdTextArea.value = data.jd;
        }

        // Visual feedback
        const notification = document.getElementById("preset-toast");
        if (notification) {
          notification.textContent = `Loaded sample: ${data.title}`;
          notification.classList.remove("hidden");
          setTimeout(() => notification.classList.add("hidden"), 3500);
        }
      } catch (err) {
        console.error("Failed to load preset", err);
      } finally {
        btn.classList.remove("opacity-50", "pointer-events-none");
      }
    });
  });
}

/**
 * Tab switching between PDF upload and manual text input
 */
function initTabSwitching() {
  const tabUpload = document.getElementById("tab-btn-upload");
  const tabText = document.getElementById("tab-btn-text");
  const paneUpload = document.getElementById("tab-pane-upload");
  const paneText = document.getElementById("tab-pane-text");

  if (!tabUpload || !tabText || !paneUpload || !paneText) return;

  tabUpload.addEventListener("click", () => {
    tabUpload.classList.add("bg-indigo-600", "text-white");
    tabUpload.classList.remove("text-gray-400", "hover:text-white");
    tabText.classList.remove("bg-indigo-600", "text-white");
    tabText.classList.add("text-gray-400", "hover:text-white");

    paneUpload.classList.remove("hidden");
    paneText.classList.add("hidden");
  });

  tabText.addEventListener("click", () => {
    tabText.classList.add("bg-indigo-600", "text-white");
    tabText.classList.remove("text-gray-400", "hover:text-white");
    tabUpload.classList.remove("bg-indigo-600", "text-white");
    tabUpload.classList.add("text-gray-400", "hover:text-white");

    paneText.classList.remove("hidden");
    paneUpload.classList.add("hidden");
  });
}

/**
 * Form Submit Spinner
 */
function initFormValidation() {
  const form = document.getElementById("screening-form");
  const submitBtn = document.getElementById("submit-btn");
  const btnText = document.getElementById("submit-btn-text");
  const btnSpinner = document.getElementById("submit-btn-spinner");

  if (!form || !submitBtn) return;

  form.addEventListener("submit", (e) => {
    const fileInput = document.getElementById("resume_file");
    const resumeText = document.getElementById("resume_text")?.value.trim() || "";
    const jdText = document.getElementById("job_description")?.value.trim() || "";

    const hasFile = fileInput && fileInput.files && fileInput.files.length > 0;

    if (!hasFile && !resumeText) {
      e.preventDefault();
      alert("Please upload a PDF resume or paste resume text.");
      return;
    }

    if (!jdText) {
      e.preventDefault();
      alert("Please enter a target Job Description.");
      return;
    }

    submitBtn.disabled = true;
    if (btnText) btnText.textContent = "Analyzing with AI & TF-IDF...";
    if (btnSpinner) btnSpinner.classList.remove("hidden");
  });
}

/**
 * Results Page Export and Copy Helpers
 */
function initExportHelpers() {
  const copyBtns = document.querySelectorAll(".copy-btn");
  copyBtns.forEach((btn) => {
    btn.addEventListener("click", () => {
      const targetText = btn.getAttribute("data-copy-target");
      if (targetText) {
        navigator.clipboard.writeText(targetText);
        const originalHtml = btn.innerHTML;
        btn.innerHTML = `<i class="bi bi-check2"></i> Copied!`;
        setTimeout(() => {
          btn.innerHTML = originalHtml;
        }, 2000);
      }
    });
  });

  const exportJsonBtn = document.getElementById("export-json-btn");
  if (exportJsonBtn && window.SCREENING_DATA) {
    exportJsonBtn.addEventListener("click", () => {
      const dataStr = "data:text/json;charset=utf-8," + encodeURIComponent(JSON.stringify(window.SCREENING_DATA, null, 2));
      const downloadAnchor = document.createElement("a");
      downloadAnchor.setAttribute("href", dataStr);
      downloadAnchor.setAttribute("download", `Screening_Analysis_${Date.now()}.json`);
      document.body.appendChild(downloadAnchor);
      downloadAnchor.click();
      downloadAnchor.remove();
    });
  }
}
