const FORMAT_HINTS = {
    code128: {
        placeholder: "Ex: REF-2026-8841",
        hint: "Accepte les lettres, chiffres et tirets (max 40 caractères)."
    },
    ean13: {
        placeholder: "Ex: 590123412345",
        hint: "Saisissez 12 chiffres (la 13e clé de contrôle est calculée automatiquement) ou 13 chiffres."
    },
    ean8: {
        placeholder: "Ex: 9638507",
        hint: "Saisissez 7 chiffres (la 8e clé de contrôle est calculée automatiquement) ou 8 chiffres."
    },
    upca: {
        placeholder: "Ex: 03600029145",
        hint: "Saisissez 11 chiffres (la 12e clé de contrôle est calculée automatiquement) ou 12 chiffres."
    }
};

function updatePlaceholder() {
    const type = document.getElementById("code_type").value;
    const refInput = document.getElementById("reference");
    const hintText = document.getElementById("format-hint");

    if (FORMAT_HINTS[type]) {
        refInput.placeholder = FORMAT_HINTS[type].placeholder;
        hintText.textContent = FORMAT_HINTS[type].hint;
    }
}

async function generateBarcode() {
    const alertBox = document.getElementById("gen_alert");
    const btn = document.getElementById("btn-generate");
    alertBox.className = "alert";

    const payload = {
        product_name: document.getElementById("product_name").value,
        code_type: document.getElementById("code_type").value,
        reference: document.getElementById("reference").value,
        format: document.getElementById("img_format").value,
        optimize: document.getElementById("optimize").checked
    };

    btn.disabled = true;
    btn.innerHTML = '<i class="ion-load-c"></i> Génération en cours...';

    try {
        const res = await fetch("/api/generate", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(payload)
        });
        const data = await res.json();

        if (!data.success) {
            alertBox.textContent = data.message;
            alertBox.classList.add("error");
            return;
        }

        alertBox.textContent = data.message;
        alertBox.classList.add("success");

        document.getElementById("preview_box").innerHTML = `
            <img src="${data.image_base64}" alt="Code-barres généré" class="barcode-result-img">
            <div class="result-specs">
                <span class="spec-tag"><strong>Code :</strong> ${data.full_code}</span>
                <span class="spec-tag"><strong>Poids :</strong> ${data.size_kb} Ko</span>
            </div>
            <a href="${data.image_base64}" download="${data.filename}" class="btn btn-download">
                <i class="ion-android-download"></i> Télécharger (${data.filename})
            </a>
        `;

        updateHistoryTable(data.history);
    } catch (error) {
        alertBox.textContent = "Erreur de communication avec le serveur Python.";
        alertBox.classList.add("error");
    } finally {
        btn.disabled = false;
        btn.innerHTML = '<i class="ion-flash"></i> Générer le code-barres';
    }
}

async function verifyBarcode() {
    const alertBox = document.getElementById("verify_alert");
    alertBox.className = "alert";

    const payload = {
        code_type: document.getElementById("verify_type").value,
        code: document.getElementById("verify_code").value
    };

    try {
        const res = await fetch("/api/verify", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(payload)
        });
        const data = await res.json();

        alertBox.textContent = data.message;
        alertBox.classList.add(data.valid ? "success" : "error");
    } catch (error) {
        alertBox.textContent = "Impossible de vérifier le code actuellement.";
        alertBox.classList.add("error");
    }
}

function updateHistoryTable(history) {
    const tbody = document.getElementById("history_body");
    const countPill = document.getElementById("history-count");

    if (countPill) {
        countPill.textContent = `${history.length} enregistrement(s)`;
    }

    if (!history || history.length === 0) {
        tbody.innerHTML = `
            <tr>
                <td colspan="6" class="empty-table">Aucun historique disponible. Générez votre premier code-barres ci-dessus.</td>
            </tr>
        `;
        return;
    }

    tbody.innerHTML = history.map(item => `
        <tr>
            <td class="text-muted">${item.date}</td>
            <td><strong>${item.product}</strong></td>
            <td><span class="norm-badge">${item.type}</span></td>
            <td><code class="code-pill">${item.full_code}</code></td>
            <td><span class="file-meta">${item.format} • ${item.size_kb} Ko</span></td>
            <td>
                <button class="btn-icon" onclick="copyCode('${item.full_code}')" title="Copier le code">
                    <i class="ion-ios-copy-outline"></i>
                </button>
            </td>
        </tr>
    `).join("");
}

function copyCode(text) {
    navigator.clipboard.writeText(text).then(() => {
        const toast = document.getElementById("toast");
        toast.textContent = `Code "${text}" copié !`;
        toast.classList.add("show");
        setTimeout(() => toast.classList.remove("show"), 2500);
    });
}
