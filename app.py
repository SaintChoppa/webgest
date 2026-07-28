import os
import shutil
from datetime import datetime
from pathlib import Path

from flask import (
    Flask, render_template, request, send_file, redirect,
    url_for, flash, abort, jsonify
)
from werkzeug.utils import secure_filename

# ---------------------------------------------------------------------------
# Configuración
# ---------------------------------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent
STORAGE_DIR = BASE_DIR / "storage"
STORAGE_DIR.mkdir(exist_ok=True)

MAX_CONTENT_LENGTH = 10 * 1024 * 1024 * 1024  # 10 GB por request (ajustable)

app = Flask(__name__)
app.secret_key = os.environ.get("FILEMANAGER_SECRET", "cambia-esta-clave-en-produccion")
app.config["MAX_CONTENT_LENGTH"] = MAX_CONTENT_LENGTH


# ---------------------------------------------------------------------------
# Helpers de seguridad: evitar path traversal (../../etc)
# ---------------------------------------------------------------------------
def safe_join(relative_path: str) -> Path:
    """Resuelve una ruta relativa dentro de STORAGE_DIR, bloqueando salidas."""
    relative_path = (relative_path or "").strip("/\\")
    candidate = (STORAGE_DIR / relative_path).resolve()
    if STORAGE_DIR.resolve() not in candidate.parents and candidate != STORAGE_DIR.resolve():
        abort(400, "Ruta inválida")
    return candidate


def human_size(num_bytes: int) -> str:
    step = 1024.0
    for unit in ["B", "KB", "MB", "GB", "TB"]:
        if num_bytes < step:
            return f"{num_bytes:.1f} {unit}"
        num_bytes /= step
    return f"{num_bytes:.1f} PB"


def list_dir(path: Path, rel: str):
    entries = []
    for item in sorted(path.iterdir(), key=lambda p: (p.is_file(), p.name.lower())):
        stat = item.stat()
        entries.append({
            "name": item.name,
            "is_dir": item.is_dir(),
            "size": human_size(stat.st_size) if item.is_file() else "-",
            "modified": datetime.fromtimestamp(stat.st_mtime).strftime("%Y-%m-%d %H:%M"),
            "rel_path": f"{rel}/{item.name}".strip("/"),
        })
    return entries


# ---------------------------------------------------------------------------
# Rutas
# ---------------------------------------------------------------------------
@app.route("/")
@app.route("/browse/")
@app.route("/browse/<path:subpath>")
def browse(subpath=""):
    current = safe_join(subpath)
    if not current.exists() or not current.is_dir():
        flash("La carpeta no existe.", "error")
        return redirect(url_for("browse"))

    entries = list_dir(current, subpath)

    # Migas de pan (breadcrumbs)
    parts = [p for p in subpath.split("/") if p]
    breadcrumbs = []
    acc = ""
    for p in parts:
        acc = f"{acc}/{p}".strip("/")
        breadcrumbs.append({"name": p, "path": acc})

    parent = "/".join(parts[:-1]) if parts else None

    return render_template(
        "index.html",
        entries=entries,
        current_path=subpath,
        breadcrumbs=breadcrumbs,
        parent=parent,
    )


@app.route("/upload/", defaults={"subpath": ""}, methods=["POST"])
@app.route("/upload/<path:subpath>", methods=["POST"])
def upload(subpath):
    target_dir = safe_join(subpath)
    files = request.files.getlist("files")
    if not files or files[0].filename == "":
        flash("No seleccionaste ningún archivo.", "error")
        return redirect(url_for("browse", subpath=subpath))

    saved = 0
    for f in files:
        filename = secure_filename(f.filename)
        if not filename:
            continue
        dest = target_dir / filename
        # evitar sobreescritura silenciosa
        counter = 1
        stem, suffix = dest.stem, dest.suffix
        while dest.exists():
            dest = target_dir / f"{stem} ({counter}){suffix}"
            counter += 1
        f.save(dest)
        saved += 1

    flash(f"{saved} archivo(s) subido(s) correctamente.", "success")
    return redirect(url_for("browse", subpath=subpath))


@app.route("/download/<path:filepath>")
def download(filepath):
    target = safe_join(filepath)
    if not target.exists() or not target.is_file():
        abort(404)
    return send_file(target, as_attachment=True)


@app.route("/mkdir/", defaults={"subpath": ""}, methods=["POST"])
@app.route("/mkdir/<path:subpath>", methods=["POST"])
def mkdir(subpath):
    name = secure_filename(request.form.get("folder_name", "").strip())
    if not name:
        flash("Nombre de carpeta inválido.", "error")
        return redirect(url_for("browse", subpath=subpath))

    target_dir = safe_join(subpath) / name
    try:
        target_dir.mkdir(exist_ok=False)
        flash("Carpeta creada.", "success")
    except FileExistsError:
        flash("Ya existe una carpeta con ese nombre.", "error")
    return redirect(url_for("browse", subpath=subpath))


@app.route("/delete/<path:filepath>", methods=["POST"])
def delete(filepath):
    target = safe_join(filepath)
    if not target.exists():
        abort(404)

    parent_rel = "/".join(filepath.split("/")[:-1])

    if target.is_dir():
        shutil.rmtree(target)
        flash("Carpeta eliminada.", "success")
    else:
        target.unlink()
        flash("Archivo eliminado.", "success")

    return redirect(url_for("browse", subpath=parent_rel))


@app.route("/rename/<path:filepath>", methods=["POST"])
def rename(filepath):
    target = safe_join(filepath)
    if not target.exists():
        abort(404)

    new_name = secure_filename(request.form.get("new_name", "").strip())
    if not new_name:
        flash("Nombre inválido.", "error")
        return redirect(request.referrer or url_for("browse"))

    new_path = target.parent / new_name
    if new_path.exists():
        flash("Ya existe un archivo/carpeta con ese nombre.", "error")
    else:
        target.rename(new_path)
        flash("Renombrado correctamente.", "success")

    parent_rel = "/".join(filepath.split("/")[:-1])
    return redirect(url_for("browse", subpath=parent_rel))


# ---------------------------------------------------------------------------
# Manejo de errores simple
# ---------------------------------------------------------------------------
@app.errorhandler(404)
def not_found(e):
    return render_template("error.html", code=404, message="No encontrado"), 404


@app.errorhandler(400)
def bad_request(e):
    return render_template("error.html", code=400, message="Solicitud inválida"), 400


if __name__ == "__main__":
    # host="0.0.0.0" para que sea accesible desde otros equipos de la LAN
    app.run(host="0.0.0.0", port=8080, debug=False)
