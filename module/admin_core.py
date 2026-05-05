import json
import os

CONFIG_FILE = "/etc/pps_bot/config.json"
BRAND = "🜲 PPS"

def get_config():
    if not os.path.exists(CONFIG_FILE):
        return {}
    with open(CONFIG_FILE, 'r') as f:
        return json.load(f)

def _save_config(cfg):
    with open(CONFIG_FILE, 'w') as f:
        json.dump(cfg, f, indent=2)

def is_super_admin(user_id):
    cfg = get_config()
    return user_id == int(cfg.get("super_admin", 0))

def list_admins():
    cfg = get_config()
    super_admin = cfg.get("super_admin", "N/A")
    admins = cfg.get("admins", [])
    lines = f"👑 Super Admin : <code>{super_admin}</code>\n\n"
    if admins:
        lines += "<b>Admins :</b>\n"
        for a in admins:
            lines += f"  • <code>{a}</code>\n"
    else:
        lines += "Aucun admin supplémentaire."
    return f"┏━━━━━━━━━━━━━━━━━━━━━━━━━━┓\n┃LISTE ADMINS DE 🜲 PPS TECH TUNNEL\n┗━━━━━━━━━━━━━━━━━━━━━━━━━━┛\n{lines}"

def approve_new_admin(target_id):
    cfg = get_config()
    target_id = int(target_id)
    if target_id == int(cfg.get("super_admin", 0)):
        return False, "C'est déjà le Super Admin."
    admins = cfg.get("admins", [])
    if target_id in admins:
        return False, f"<code>{target_id}</code> est déjà admin."
    admins.append(target_id)
    cfg["admins"] = admins
    _save_config(cfg)
    return True, f"<code>{target_id}</code> ajouté comme admin."

def remove_admin(target_id):
    cfg = get_config()
    target_id = int(target_id)
    admins = cfg.get("admins", [])
    if target_id not in admins:
        return False, f"<code>{target_id}</code> n'est pas admin."
    admins.remove(target_id)
    cfg["admins"] = admins
    _save_config(cfg)
    return True, f"<code>{target_id}</code> révoqué."

def promote_admin_to_supreme(target_id):
    cfg = get_config()
    admins = cfg.get("admins", [])
    if target_id not in admins:
        return False, f"<code>{target_id}</code> n'est pas dans la liste des admins."
    cfg["super_admin"] = target_id
    admins = [a for a in admins if a != target_id]
    cfg["admins"] = admins
    _save_config(cfg)
    return True, f"<code>{target_id}</code> promu Super Admin."