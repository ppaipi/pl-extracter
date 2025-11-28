document.getElementById("processBtn").addEventListener("click", async () => {
    const fileInput = document.getElementById("pdfFile");
    const status = document.getElementById("status");

    if (!fileInput.files.length) {
        status.textContent = "Subí un PDF primero.";
        return;
    }

    status.textContent = "Procesando...";

    const formData = new FormData();
    formData.append("file", fileInput.files[0]);

    const res = await fetch("https://pl-extracter.onrender.com/extract", {
        method: "POST",
        body: formData
    });

    if (!res.ok) {
        status.textContent = "Error procesando el PDF.";
        return;
    }

    const blob = await res.blob();
    const url = URL.createObjectURL(blob);

    const a = document.createElement("a");
    a.href = url;
    a.download = "resultado.xlsx";
    a.click();

    status.textContent = "¡Listo! Excel descargado.";
});
