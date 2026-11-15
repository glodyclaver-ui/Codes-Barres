import io
import os
import json
import base64
from datetime import datetime
from flask import Flask, render_template, request, jsonify
import barcode
from barcode.writer import ImageWriter
from PIL import Image

app = Flask(__name__)
HISTORY_FILE = "historique_codes.json"


def load_history():
    """Charge l'historique local des codes-barres générés."""
    if os.path.exists(HISTORY_FILE):
        try:
            with open(HISTORY_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            return []
    return []


def save_to_history(entry):
    """Enregistre un nouveau code dans le journal local (max 100 entrées)."""
    history = load_history()
    history.insert(0, entry)
    with open(HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump(history[:100], f, indent=4, ensure_ascii=False)


def validate_barcode_data(code_type, data):
    """Vérifie la conformité de la référence selon le standard choisi."""
    data = data.strip()
    if not data:
        return False, "La référence produit ne peut pas être vide."

    if code_type == "ean13":
        if not data.isdigit() or len(data) not in (12, 13):
            return False, "Un code EAN-13 doit contenir exactement 12 ou 13 chiffres."
    elif code_type == "ean8":
        if not data.isdigit() or len(data) not in (7, 8):
            return False, "Un code EAN-8 doit contenir exactement 7 ou 8 chiffres."
    elif code_type == "upca":
        if not data.isdigit() or len(data) not in (11, 12):
            return False, "Un code UPC-A doit contenir exactement 11 ou 12 chiffres."
    elif code_type == "code128":
        if len(data) > 40:
            return False, "La référence Code 128 ne doit pas dépasser 40 caractères."
    else:
        return False, f"Norme de code-barres non prise en charge : {code_type}"

    return True, "Référence valide et conforme au standard."


def generate_barcode_image(code_type, data, img_format="PNG", optimize=True):
    """Génère l'image du code-barres en mémoire vive et l'optimise."""
    barcode_class = barcode.get_barcode_class(code_type)
    writer = ImageWriter()

    raw_buffer = io.BytesIO()
    my_barcode = barcode_class(data, writer=writer)
    my_barcode.write(raw_buffer, options={
        "module_width": 0.3,
        "module_height": 12.0,
        "font_size": 10,
        "text_distance": 4.0,
        "quiet_zone": 3.0
    })
    raw_buffer.seek(0)

    img = Image.open(raw_buffer)
    final_buffer = io.BytesIO()
    fmt = img_format.upper()

    if fmt in ("JPG", "JPEG"):
        img = img.convert("RGB")
        quality = 75 if optimize else 95
        img.save(final_buffer, format="JPEG", quality=quality, optimize=True)
        mime = "image/jpeg"
        ext = "jpg"
    elif fmt == "WEBP":
        quality = 75 if optimize else 95
        img.save(final_buffer, format="WEBP", quality=quality, method=6)
        mime = "image/webp"
        ext = "webp"
    else:
        if optimize:
            img = img.convert("P", palette=Image.ADAPTIVE, colors=8)
        img.save(final_buffer, format="PNG", optimize=True)
        mime = "image/png"
        ext = "png"

    final_buffer.seek(0)
    full_code = my_barcode.get_fullcode()
    return final_buffer, mime, ext, full_code


@app.route("/")
def index():
    """Affiche l'interface principale avec l'historique local."""
    return render_template("index.html", history=load_history())


@app.route("/api/generate", methods=["POST"])
def api_generate():
    """Endpoint API : valide, génère l'image optimisée et journalise le code."""
    payload = request.get_json(silent=True) or {}
    product_name = payload.get("product_name", "Produit sans nom").strip()
    code_type = payload.get("code_type", "code128").lower()
    reference = payload.get("reference", "").strip()
    img_format = payload.get("format", "PNG").upper()
    optimize = bool(payload.get("optimize", True))

    is_valid, message = validate_barcode_data(code_type, reference)
    if not is_valid:
        return jsonify({"success": False, "message": message}), 400

    try:
        buffer, mime, ext, full_code = generate_barcode_image(
            code_type, reference, img_format, optimize
        )
        img_bytes = buffer.getvalue()
        size_kb = round(len(img_bytes) / 1024, 2)
        b64_img = base64.b64encode(img_bytes).decode("utf-8")

        record = {
            "id": datetime.now().strftime("%Y%m%d%H%M%S"),
            "date": datetime.now().strftime("%d/%m/%Y %H:%M"),
            "product": product_name or "Non spécifié",
            "type": code_type.upper(),
            "reference_input": reference,
            "full_code": full_code,
            "format": ext.upper(),
            "size_kb": size_kb
        }
        save_to_history(record)

        return jsonify({
            "success": True,
            "message": f"Code validé et généré ({full_code})",
            "image_base64": f"data:{mime};base64,{b64_img}",
            "filename": f"barcode_{full_code}.{ext}",
            "size_kb": size_kb,
            "full_code": full_code,
            "history": load_history()
        })

    except Exception as e:
        return jsonify({"success": False, "message": f"Erreur technique : {str(e)}"}), 500


@app.route("/api/verify", methods=["POST"])
def api_verify():
    """Endpoint API : vérifie la clé de contrôle et l'existence dans le suivi local."""
    payload = request.get_json(silent=True) or {}
    code_type = payload.get("code_type", "ean13").lower()
    code = payload.get("code", "").strip()

    is_valid, msg = validate_barcode_data(code_type, code)
    if not is_valid:
        return jsonify({"valid": False, "message": msg})

    try:
        barcode_class = barcode.get_barcode_class(code_type)
        obj = barcode_class(code)
        expected_code = obj.get_fullcode()

        if len(code) == len(expected_code) and code != expected_code:
            return jsonify({
                "valid": False,
                "message": f"Clé de contrôle invalide ! Le code conforme est : {expected_code}"
            })

        history = load_history()
        found = next((item for item in history if item["full_code"] == expected_code), None)
        status_msg = f"Code {code_type.upper()} valide ({expected_code})."
        if found:
            status_msg += f" Associé au produit : « {found['product']} » (généré le {found['date']})."
        else:
            status_msg += " Non répertorié dans l'historique local."

        return jsonify({"valid": True, "message": status_msg})
    except Exception as e:
        return jsonify({"valid": False, "message": f"Code invalide : {str(e)}"})


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)
