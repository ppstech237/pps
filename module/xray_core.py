import subprocess
import re
import os

XRAY_CONFIG = "/etc/xray/config.json"

def _user_exists(username):
    """Vérifie si l'utilisateur existe déjà dans la config Xray"""
    if not os.path.exists(XRAY_CONFIG):
        return False
    with open(XRAY_CONFIG, 'r') as f:
        content = f.read()
    # Recherche du pattern ### username date uuid
    if re.search(rf'### {username} \d{{4}}-\d{{2}}-\d{{2}} [a-f0-9-]+', content):
        return True
    # Recherche du pattern "email": "username"
    if re.search(rf'"email": "{username}"', content):
        return True
    return False

def _exec_script(proto, action, username="", days=""):
    """
    Exécute le script shell du protocole et retourne la sortie brute.
    N'utilise que les commandes existantes dans /usr/local/sbin/
    """
    if action == "create":
        cmd = f'printf "1\n{username}\n{days}\n" | {proto}'
    elif action == "renew":
        cmd = f'printf "2\n{username}\n{days}\n" | {proto}'
    elif action == "delete":
        cmd = f'printf "3\n{username}\n" | {proto}'
    elif action == "list":
        cmd = f'printf "4\n" | {proto}'
    elif action == "detail":
        cmd = f'printf "4\n{username}\n" | {proto}'
    else:
        return None
    
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=30)
        return result.stdout
    except Exception:
        return None

def _clean_output(raw_output):
    """
    Nettoie la sortie du script shell pour l'affichage dans le bot.
    Supprime les menus, les invites, et formate les liens.
    """
    if not raw_output:
        return "❌ Aucune réponse du serveur."
    
    lines = raw_output.split('\n')
    cleaned = []
    skip_next = False
    
    for line in lines:
        # Supprimer les lignes de menu et d'interaction
        if "Select menu" in line or "Press any key" in line:
            continue
        if "option :" in line.lower() or "Input Username" in line:
            continue
        if "Validity (days)" in line or "Username cannot be empty" in line:
            continue
        if "not found" in line.lower() and "username" in line.lower():
            continue
        if "Enter username" in line or "Expiry days must be" in line:
            continue
        
        # Remplacer la ligne de séparation
        if "●━━━━━━━━━━━━━━━━━━━━ 🜲 PPS_TECH ━━━━━━━━━━━━━━━━━━━━●" in line:
            cleaned.append("●━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━●")
            continue
        
        # Formater les liens avec <code> pour copie facile
        if "vless://" in line or "vmess://" in line or "trojan://" in line or "ss://" in line:
            # Extraire le lien et le nettoyer
            link = line.strip()
            # Supprimer le préfixe ┃ si présent
            link = re.sub(r'^[┃\s]+', '', link)
            if link.startswith(("vless://", "vmess://", "trojan://", "ss://")):
                cleaned.append(f"┃ <code>{link}</code>")
            else:
                cleaned.append(line)
        else:
            cleaned.append(line)
    
    # Nettoyer les lignes vides en trop
    result = []
    for line in cleaned:
        if line.strip() or (result and result[-1].strip()):
            result.append(line)
    
    return "\n".join(result)

def create_xray_account(proto, username, days, created_by_id=None):
    """
    Crée un compte Xray (VMESS, VLESS, TROJAN, SOCKS)
    via les scripts shell existants.
    """
    # Vérifier si l'utilisateur existe déjà
    if _user_exists(username):
        return False, f"❌ L'utilisateur <code>{username}</code> existe déjà."
    
    # Exécuter la création
    raw_output = _exec_script(proto, "create", username, days)
    
    if not raw_output:
        return False, f"❌ Erreur lors de la création du compte {proto.upper()}. Vérifiez que le script '{proto}' est installé."
    
    # Vérifier si la création a réussi
    if "already exists" in raw_output.lower():
        return False, f"❌ L'utilisateur <code>{username}</code> existe déjà."
    
    if "Invalid selection" in raw_output:
        return False, f"❌ Le script {proto} n'a pas reconnu la commande."
    
    # Nettoyer et formater la sortie
    clean_output = _clean_output(raw_output)
    
    # Ajouter la mention développé par si absente
    if "Développé par" not in clean_output:
        clean_output += "\n━━━━━━━━━━━━━━━━━━━━━━━━\n✅ Développé par 🜲 PPS TECH.✅\n ━━━━━━━━━━━━━━━━━━━━━━━━\n●━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━●"
    
    return True, clean_output

def renew_xray_account(proto, username, days):
    """Renouvelle un compte Xray existant"""
    if not _user_exists(username):
        return False, f"❌ L'utilisateur <code>{username}</code> n'existe pas."
    
    raw_output = _exec_script(proto, "renew", username, days)
    
    if not raw_output:
        return False, f"❌ Erreur lors du renouvellement du compte {proto.upper()}."
    
    clean_output = _clean_output(raw_output)
    return True, clean_output

def delete_xray_account(proto, username):
    """Supprime un compte Xray"""
    if not _user_exists(username):
        return False, f"❌ L'utilisateur <code>{username}</code> n'existe pas."
    
    raw_output = _exec_script(proto, "delete", username)
    
    if not raw_output:
        return False, f"❌ Erreur lors de la suppression du compte {proto.upper()}."
    
    clean_output = _clean_output(raw_output)
    return True, clean_output

def get_xray_usernames(proto):
    """Retourne la liste des noms d'utilisateurs Xray"""
    raw_output = _exec_script(proto, "list")
    if not raw_output:
        return []
    
    # Extraire les noms du format: ┃ username 2026-05-06
    users = re.findall(r'[┃│]\s*([a-zA-Z0-9_-]+)\s+\d{4}-\d{2}-\d{2}', raw_output)
    # Ajouter les noms du format ### username date uuid
    users += re.findall(r'### ([a-zA-Z0-9_-]+) \d{4}-\d{2}-\d{2}', raw_output)
    
    return list(set(users))

def get_xray_account_details(proto, username):
    """Affiche les détails d'un compte Xray"""
    if not _user_exists(username):
        return False, f"❌ L'utilisateur <code>{username}</code> n'existe pas."
    
    raw_output = _exec_script(proto, "detail", username)
    
    if not raw_output:
        return False, f"❌ Erreur lors de la récupération des détails."
    
    clean_output = _clean_output(raw_output)
    return True, clean_output
