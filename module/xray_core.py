import subprocess
import json
import uuid
import os
import re
from datetime import datetime, timedelta

XRAY_CONFIG = "/etc/xray/config.json"

def _load_config():
    if not os.path.exists(XRAY_CONFIG):
        return None
    with open(XRAY_CONFIG, 'r') as f:
        return json.load(f)

def _save_config(cfg):
    with open(XRAY_CONFIG, 'w') as f:
        json.dump(cfg, f, indent=2)
    subprocess.run("systemctl restart xray", shell=True)

def create_xray_account(proto, username, days, created_by_id=None):
    """Crée un compte Xray directement (sans passer par les menus interactifs)"""
    
    # Vérifier si l'utilisateur existe
    with open(XRAY_CONFIG, 'r') as f:
        content = f.read()
    
    if re.search(rf'(### {username}|\"email\": \"{username}\")', content):
        return False, f"❌ L'utilisateur <code>{username}</code> existe déjà."
    
    # Générer UUID
    new_uuid = str(uuid.uuid4())
    expiry = (datetime.now() + timedelta(days=days)).strftime("%Y-%m-%d")
    
    domain = subprocess.getoutput("cat /etc/xray/domain 2>/dev/null || echo 'N/A'")
    ip = subprocess.getoutput("curl -s ifconfig.me")
    
    # Ajouter selon le protocole
    if proto == "vmess":
        # Ajouter dans l'inbound vmess (port 23456 ou 2025)
        sed_cmd = f'''sed -i '/#vmess$/a\\### {username} {expiry} {new_uuid}\n}},{{\n  "id": "{new_uuid}",\n  "alterId": 0,\n  "email": "{username}"\n  #vmess' {XRAY_CONFIG}'''
        subprocess.run(sed_cmd, shell=True)
        
        # Générer les liens
        ws_tls = f'{{"v":"2","ps":"{username}","add":"{domain}","port":"443","id":"{new_uuid}","aid":"0","net":"ws","path":"/vmess","type":"none","host":"","tls":"tls"}}'
        ws_nontls = f'{{"v":"2","ps":"{username}","add":"{domain}","port":"80","id":"{new_uuid}","aid":"0","net":"ws","path":"/vmess","type":"none","host":"","tls":"none"}}'
        grpc = f'{{"v":"2","ps":"{username}","add":"{domain}","port":"443","id":"{new_uuid}","aid":"0","net":"grpc","path":"vmess-grpc","type":"none","host":"","tls":"tls"}}'
        
        link_tls = "vmess://" + subprocess.getoutput(f"echo '{ws_tls}' | base64 -w 0")
        link_nontls = "vmess://" + subprocess.getoutput(f"echo '{ws_nontls}' | base64 -w 0")
        link_grpc = "vmess://" + subprocess.getoutput(f"echo '{grpc}' | base64 -w 0")
        
        output = f"""┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ Username    : {username}
┃ Expiry Date : {expiry}
┃ UUID        : {new_uuid}
●━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━●
┃ Domain      : {domain}
┃ Port TLS    : 443
┃ Port NonTLS : 80
┃ Port gRPC   : 443
┃ alterId     : 0
┃ Security    : auto
┃ Network     : ws
┃ Path        : /vmess
●━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━●
┃ TLS  :
┃ {link_tls}
┃
┃ NTLS :
┃ {link_nontls}
┃
┃ GRPC :
┃ {link_grpc}
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛
●━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━●"""
        
    elif proto == "vless":
        sed_cmd = f'''sed -i '/#vless$/a\\  {{\n    "id": "{new_uuid}",\n    "email": "{username}"\n  }},\n#vless' {XRAY_CONFIG}'''
        subprocess.run(sed_cmd, shell=True)
        
        link_tls = f"vless://{new_uuid}@{domain}:443?path=/vless&security=tls&encryption=none&type=ws#{username}"
        link_nontls = f"vless://{new_uuid}@{domain}:80?path=/vless&encryption=none&type=ws#{username}"
        link_grpc = f"vless://{new_uuid}@{domain}:443?mode=gun&security=tls&encryption=none&type=grpc&serviceName=vless-grpc#{username}"
        
        output = f"""┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ Username    : {username}
┃ Expiry Date : {expiry}
┃ UUID        : {new_uuid}
●━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━●
┃ Domain      : {domain}
┃ Port TLS    : 443
┃ Port NonTLS : 80
┃ Port gRPC   : 443
┃ Security    : auto
┃ Network     : ws
┃ Path        : /vless
●━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━●
┃ TLS  :
┃ {link_tls}
┃
┃ NTLS :
┃ {link_nontls}
┃
┃ GRPC :
┃ {link_grpc}
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛
●━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━●"""
    
    elif proto == "trojan":
        sed_cmd = f'''sed -i '/#trojanws$/a\\  {{\n    "password": "{new_uuid}",\n    "email": "{username}"\n  }},\n#trojanws' {XRAY_CONFIG}'''
        subprocess.run(sed_cmd, shell=True)
        
        link_tls = f"trojan://{new_uuid}@{domain}:443?path=/trws&security=tls&type=ws#{username}"
        link_nontls = f"trojan://{new_uuid}@{domain}:80?path=/trws&type=ws#{username}"
        link_grpc = f"trojan://{new_uuid}@{domain}:443?mode=gun&security=tls&type=grpc&serviceName=trojan-grpc#{username}"
        
        output = f"""┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ Username    : {username}
┃ Expiry Date : {expiry}
┃ Password    : {new_uuid}
●━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━●
┃ Domain      : {domain}
┃ Port TLS    : 443
┃ Port NonTLS : 80
┃ Port gRPC   : 443
┃ Path        : /trws
●━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━●
┃ TLS  :
┃ {link_tls}
┃
┃ NTLS :
┃ {link_nontls}
┃
┃ GRPC :
┃ {link_grpc}
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛
●━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━●"""
    
    elif proto == "socks":
        sed_cmd = f'''sed -i '/#ssws$/a\\  {{\n    "method": "aes-128-gcm",\n    "password": "{new_uuid}",\n    "email": "{username}"\n  }},\n#ssws' {XRAY_CONFIG}'''
        subprocess.run(sed_cmd, shell=True)
        
        link = f"ss://aes-128-gcm:{new_uuid}@{domain}:443?path=/ssws&security=tls&type=ws#{username}"
        
        output = f"""┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ Username    : {username}
┃ Expiry Date : {expiry}
┃ Password    : {new_uuid}
●━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━●
┃ Domain      : {domain}
┃ Port TLS    : 443
┃ Port NonTLS : 80
┃ Path        : /ssws
●━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━●
┃ Link :
┃ {link}
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛
●━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━●"""
    
    else:
        return False, f"❌ Protocole {proto} inconnu"
    
    # Redémarrer Xray
    subprocess.run("systemctl restart xray", shell=True)
    
    return True, output


def renew_xray_account(proto, username, days):
    """Renouvelle un compte Xray"""
    with open(XRAY_CONFIG, 'r') as f:
        content = f.read()
    
    # Chercher l'utilisateur
    pattern = rf'### {username} (\d{{4}}-\d{{2}}-\d{{2}}) ([a-f0-9-]+)'
    match = re.search(pattern, content)
    if not match:
        return False, f"❌ Utilisateur <code>{username}</code> introuvable."
    
    old_expiry = match.group(1)
    old_uuid = match.group(2)
    new_expiry = (datetime.now() + timedelta(days=days)).strftime("%Y-%m-%d")
    
    # Remplacer la date
    new_content = re.sub(rf'### {username} {old_expiry} {old_uuid}', f'### {username} {new_expiry} {old_uuid}', content)
    
    with open(XRAY_CONFIG, 'w') as f:
        f.write(new_content)
    
    subprocess.run("systemctl restart xray", shell=True)
    
    return True, f"✅ Compte <code>{username}</code> renouvelé jusqu'au <b>{new_expiry}</b>."


def delete_xray_account(proto, username):
    """Supprime un compte Xray"""
    with open(XRAY_CONFIG, 'r') as f:
        content = f.read()
    
    # Supprimer le bloc de l'utilisateur
    pattern = rf'(?s)### {username} \d{{4}}-\d{{2}}-\d{{2}} [a-f0-9-]+.*?\n(?=###|}}|#|$)'
    new_content = re.sub(pattern, '', content)
    
    if new_content == content:
        pattern = rf'"email": "{username}".*?\n(.*?)\n'
        new_content = re.sub(pattern, '', content)
    
    with open(XRAY_CONFIG, 'w') as f:
        f.write(new_content)
    
    subprocess.run("systemctl restart xray", shell=True)
    
    return True, f"✅ Compte <code>{username}</code> supprimé."


def get_xray_usernames(proto):
    """Liste les noms d'utilisateurs Xray"""
    with open(XRAY_CONFIG, 'r') as f:
        content = f.read()
    
    users = re.findall(r'### ([a-zA-Z0-9_-]+) \d{4}-\d{2}-\d{2} [a-f0-9-]+', content)
    users += re.findall(r'"email": "([a-zA-Z0-9_-]+)"', content)
    
    return list(set(users))


def get_xray_account_details(proto, username):
    """Affiche les détails d'un compte Xray"""
    with open(XRAY_CONFIG, 'r') as f:
        content = f.read()
    
    pattern = rf'### {username} (\d{{4}}-\d{{2}}-\d{{2}}) ([a-f0-9-]+)'
    match = re.search(pattern, content)
    
    if match:
        expiry = match.group(1)
        uuid_val = match.group(2)
        
        return True, f"""┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ Username    : {username}
┃ Expiry Date : {expiry}
┃ UUID        : {uuid_val}
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛
●━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━●"""
    
    return False, f"❌ Utilisateur <code>{username}</code> introuvable."
