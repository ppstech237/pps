import json
import subprocess
import uuid
import os
from datetime import datetime, timedelta

XRAY_CONFIG = "/etc/xray/config.json"
BRAND = "🜲 PPS TECH"

def _load_config():
    if not os.path.exists(XRAY_CONFIG):
        return None
    with open(XRAY_CONFIG, 'r') as f:
        return json.load(f)

def _save_config(cfg):
    with open(XRAY_CONFIG, 'w') as f:
        json.dump(cfg, f, indent=2)
    subprocess.run("systemctl restart xray", shell=True)

def _get_inbound(cfg, proto):
    for inbound in cfg.get("inbounds", []):
        tag = inbound.get("tag", "").lower()
        if proto in tag:
            return inbound
    return None

def create_xray_account(proto, username, days, created_by_id=None):
    cfg = _load_config()
    if not cfg:
        return False, "❌ Fichier xray config introuvable."
    inbound = _get_inbound(cfg, proto)
    if not inbound:
        return False, f"❌ Inbound <b>{proto.upper()}</b> introuvable dans xray config."
    clients = inbound.get("settings", {}).get("clients", [])
    for c in clients:
        if c.get("email") == username:
            return False, f"❌ Compte <code>{username}</code> existe déjà."
    expiry_ms = int((datetime.now() + timedelta(days=days)).timestamp() * 1000)
    new_client = {
        "id": str(uuid.uuid4()),
        "email": username,
        "expiryTime": expiry_ms
    }
    clients.append(new_client)
    inbound["settings"]["clients"] = clients
    _save_config(cfg)
    ip = subprocess.getoutput("curl -s ifconfig.me").strip()
    domain = subprocess.getoutput("cat /etc/xray/domain 2>/dev/null || echo 'N/A'").strip()
    expiry_str = (datetime.now() + timedelta(days=days)).strftime("%Y-%m-%d")
    return True, (
        f"┏━━━━━━━━━━━━━━━━━━━━━━━━━━┓\n"
        f"┃     {proto.upper()} ACCOUNT \n"
        f"┗━━━━━━━━━━━━━━━━━━━━━━━━━━┛\n"
        f"👤 Username: <code>{username}</code>\n"
        f"🔑 UUID: <code>{new_client['id']}</code>\n"
        f"⏳ Expiry: <code>{expiry_str}</code>\n"
        f"🖥️ IP: <code>{ip}</code>\n"
        f"🌐 Domain: <code>{domain}</code>\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"✅ Développé par 🜲 PPS TECH.✅\n"
        f" ━━━━━━━━━━━━━━━━━━━━━━━━"
    )

def renew_xray_account(proto, username, days):
    cfg = _load_config()
    if not cfg:
        return False, "❌ Fichier xray config introuvable."
    inbound = _get_inbound(cfg, proto)
    if not inbound:
        return False, f"❌ Inbound {proto.upper()} introuvable."
    clients = inbound.get("settings", {}).get("clients", [])
    for c in clients:
        if c.get("email") == username:
            expiry_ms = int((datetime.now() + timedelta(days=days)).timestamp() * 1000)
            c["expiryTime"] = expiry_ms
            inbound["settings"]["clients"] = clients
            _save_config(cfg)
            expiry_str = (datetime.now() + timedelta(days=days)).strftime("%Y-%m-%d")
            return True, f"✅ Compte <code>{username}</code> renouvelé jusqu'au <b>{expiry_str}</b>."
    return False, f"❌ Compte <code>{username}</code> introuvable."

def delete_xray_account(proto, username):
    cfg = _load_config()
    if not cfg:
        return False, "❌ Fichier xray config introuvable."
    inbound = _get_inbound(cfg, proto)
    if not inbound:
        return False, f"❌ Inbound {proto.upper()} introuvable."
    clients = inbound.get("settings", {}).get("clients", [])
    new_clients = [c for c in clients if c.get("email") != username]
    if len(new_clients) == len(clients):
        return False, f"❌ Compte <code>{username}</code> introuvable."
    inbound["settings"]["clients"] = new_clients
    _save_config(cfg)
    return True, f"✅ Compte <code>{username}</code> supprimé."

def get_xray_usernames(proto):
    cfg = _load_config()
    if not cfg:
        return []
    inbound = _get_inbound(cfg, proto)
    if not inbound:
        return []
    clients = inbound.get("settings", {}).get("clients", [])
    return [c.get("email", "?") for c in clients]

def get_xray_account_details(proto, username):
    cfg = _load_config()
    if not cfg:
        return False, "❌ Fichier xray config introuvable."
    inbound = _get_inbound(cfg, proto)
    if not inbound:
        return False, f"❌ Inbound {proto.upper()} introuvable."
    for c in inbound.get("settings", {}).get("clients", []):
        if c.get("email") == username:
            expiry_ms = c.get("expiryTime", 0)
            if expiry_ms:
                expiry_str = datetime.fromtimestamp(expiry_ms / 1000).strftime("%Y-%m-%d")
            else:
                expiry_str = "Illimité"
            return True, (
                f"┏━━━━━━━━━━━━━━━━━━━━━━━━━━┓\n"
                f"┃      DÉTAILS {proto.upper()} \n"
                f"┗━━━━━━━━━━━━━━━━━━━━━━━━━━┛\n"
                f"👤 Username : <code>{username}</code>\n"
                f"🔑 UUID     : <code>{c.get('id','N/A')}</code>\n"
                f"📅 Expiry   : <code>{expiry_str}</code>"
                f"━━━━━━━━━━━━━━━━━━━━━━━━\n"
                f"✅ Développé par 🜲 PPS TECH.✅\n"
                f" ━━━━━━━━━━━━━━━━━━━━━━━━"
            )
    return False, f"❌ Compte <code>{username}</code> introuvable."