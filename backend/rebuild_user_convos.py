import json
from pathlib import Path

# === Configura rutas ===
base_dir = Path(r"C:\Users\carlo\chat-multiagent-clean2\backend\data\v2")
convos_dir = base_dir / "convos"
users_dir = base_dir / "users"

# === Usuario objetivo ===
user_name = "carlos"  # minúsculas
user_dir = users_dir / user_name
user_dir.mkdir(parents=True, exist_ok=True)

# === Archivo de salida ===
output_path = user_dir / "user_convos_list.json"

# === Reconstruir lista ===
convos = []
for convo_file in convos_dir.glob("*.json"):
    convo_id = convo_file.stem
    try:
        with open(convo_file, "r", encoding="utf-8") as f:
            data = json.load(f)
        created_at = data.get("created_at") or "unknown"
        convos.append({"convo_id": convo_id, "created_at": created_at})
    except Exception as e:
        print(f"⚠️ Error con {convo_file.name}: {e}")

# === Guardar lista ordenada ===
convos.sort(key=lambda x: x["created_at"], reverse=True)
with open(output_path, "w", encoding="utf-8") as f:
    json.dump(convos, f, indent=2)

print(f"✅ Archivo generado: {output_path}")
print(f"🗂️ Conversaciones detectadas: {len(convos)}")
