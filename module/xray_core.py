import subprocess
import re

def _run_script(proto, action, username="", days=""):
    """Exécute un script panel et retourne sa sortie nettoyée"""
    if action == "add":
        cmd = f'echo -e "1\n{username}\n{days}\n" | {proto}'
    elif action == "renew":
        cmd = f'echo -e "2\n{username}\n{days}\n" | {proto}'
    elif action == "del":
        cmd = f'echo -e "3\n{username}\n" | {proto}'
    elif action == "list":
        cmd = f'echo -e "4\n" | {proto}'
    else:
        return False, "Action inconnue"
    
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    output = result.stdout
    
    # Nettoyer la sortie
    lines = output.split('\n')
    cleaned = []
    for line in lines:
        # Supprimer les lignes de menu et d'interaction
        if "Select menu" in line or "Press any key" in line:
            continue
        if "option :" in line.lower() or "input username" in line.lower():
            continue
        if "validity (days)" in line.lower() or "enter username" in line.lower():
            continue
        if "not found" in line.lower() and "username" in line.lower():
            continue
        
        # Remplacer la ligne de séparation
        if "●━━━━━━━━━━━━━━━━━━━━ 🜲 PPS_TECH ━━━━━━━━━━━━━━━━━━━━●" in line:
            cleaned.append("●━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━●")
        else:
            cleaned.append(line)
    
    # Nettoyer les lignes vides au début et à la fin
    while cleaned and not cleaned[0].strip():
        cleaned.pop(0)
    while cleaned and not cleaned[-1].strip():
        cleaned.pop()
    
    return True, "\n".join(cleaned)

def create_xray_account(proto, username, days, created_by_id=None):
    if proto == "vless":
        return _run_script("vless", "add", username, days)
    elif proto == "vmess":
        return _run_script("vmess", "add", username, days)
    elif proto == "trojan":
        return _run_script("trojan", "add", username, days)
    elif proto == "socks":
        return _run_script("socks", "add", username, days)
    else:
        return False, f"❌ Protocole {proto} inconnu"

def renew_xray_account(proto, username, days):
    if proto == "vless":
        return _run_script("vless", "renew", username, days)
    elif proto == "vmess":
        return _run_script("vmess", "renew", username, days)
    elif proto == "trojan":
        return _run_script("trojan", "renew", username, days)
    elif proto == "socks":
        return _run_script("socks", "renew", username, days)
    else:
        return False, f"❌ Protocole {proto} inconnu"

def delete_xray_account(proto, username):
    if proto == "vless":
        return _run_script("vless", "del", username)
    elif proto == "vmess":
        return _run_script("vmess", "del", username)
    elif proto == "trojan":
        return _run_script("trojan", "del", username)
    elif proto == "socks":
        return _run_script("socks", "del", username)
    else:
        return False, f"❌ Protocole {proto} inconnu"

def get_xray_usernames(proto):
    success, output = _run_script(proto, "list")
    if not success:
        return []
    # Extraire les noms d'utilisateurs de la liste
    users = []
    for line in output.split('\n'):
        # Chercher les lignes qui contiennent des noms d'utilisateurs
        match = re.search(r'┃\s*([a-zA-Z0-9_-]+)\s+\d{4}-\d{2}-\d{2}', line)
        if match:
            users.append(match.group(1))
    return users

def get_xray_account_details(proto, username):
    # Pour les détails, le mieux est d'utiliser l'option 4 (view) du panel
    cmd = f'echo -e "4\n{username}\n" | {proto}'
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    output = result.stdout
    
    # Nettoyer comme avant
    lines = output.split('\n')
    cleaned = []
    for line in lines:
        if "Select menu" in line or "Press any key" in line:
            continue
        if "option :" in line.lower():
            continue
        if "●━━━━━━━━━━━━━━━━━━━━ 🜲 PPS_TECH ━━━━━━━━━━━━━━━━━━━━●" in line:
            cleaned.append("●━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━●")
        else:
            cleaned.append(line)
    
    return True, "\n".join(cleaned)
