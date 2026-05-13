import subprocess
from datetime import datetime, timedelta

BRAND = "🜲 PPS TECH"

def _run(cmd):
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    return result.returncode, result.stdout.strip(), result.stderr.strip()

def create_ssh_account(username, password, days, created_by_id=None):
    expiry = (datetime.now() + timedelta(days=days)).strftime("%Y-%m-%d")
    rc, out, err = _run(f"id {username} 2>/dev/null")
    if rc == 0:
        return False, f"❌ L'utilisateur <code>{username}</code> existe déjà."
    _run(f"useradd -e {expiry} -s /bin/false -M {username}")
    _run(f"echo '{username}:{password}' | chpasswd")
    ip          = subprocess.getoutput("curl -s ifconfig.me").strip()
    domain      = subprocess.getoutput("cat /etc/xray/domain 2>/dev/null || echo 'N/A'").strip()
    slowdns_pub = subprocess.getoutput("cat /etc/slowdns/server.pub 2>/dev/null || echo 'N/A'").strip()
    ns_domain   = subprocess.getoutput("cat /etc/slowdns/nsdomain 2>/dev/null || echo 'N/A'").strip()
    return True, (
        f"┏━━━━━━━━━━━━━━━━━━━━━━━━━━┓\n"
        f"┃       SSH ACCOUNT DETAILS\n"
        f"┗━━━━━━━━━━━━━━━━━━━━━━━━━━┛\n"
        f"👤 Username: <code>{username}</code>\n"
        f"🔑 Password: <code>{password}</code>\n"
        f"⏳ Expiry: <code>{expiry}</code>\n"
        f"🖥️ IP: <code>{ip}</code>\n"
        f"🌐 Host: <code>{domain}</code>\n"
        f"🔌 Port SSH: <code>8880</code>\n"
        f"🔌 Port Dropbear: <code>8880</code>\n"
        f"🔌 Port WS: <code>8880</code>\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"     SLOW DNS ACCOUNT\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"🌐 Domain: <code>{domain}</code>\n"
        f"📛 NS Domain: <code>{ns_domain}</code>\n"
        f"🔌 Port DNS: <code>53</code>\n"
        f"🔥 PUB Key:\n<code>{slowdns_pub}</code>\n"
        f" ━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"📡 Format UDP Custom :\n\n"
        f"<code>{ip}:1-65535@{username}:{password}</code>\n\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"📋 Informations complètes :\n"
        f"Port OpenSSH     : 8880\n"
        f"Port UDP-Custom  : 1-65535\n"
        f"Port SSH WS      : 8880\n"
        f"Port SSH SSL WS  : 443\n"
        f"Port SSL/TLS     : 443\n"
        f"Port OVPN WS SSL : 443\n"
        f"Port OVPN SSL    : 443\n"
        f"Port OVPN TCP    : 443, 1194\n"
        f"Port OVPN UDP    : 2200\n"
        f"BadVPN UDP       : 7100, 7200, 7300\n"
        f"OpenVPN WS SSL   : https://{domain}:81/{domain}-ws-ssl.ovpn\n"
        f"OpenVPN SSL      : https://{domain}:81/{domain}-ssl.ovpn\n"
        f"OpenVPN TCP      : https://{domain}:81/{domain}-tcp.ovpn\n"
        f"OpenVPN UDP      : https://{domain}:81/{domain}-udp.ovpn\n"
        f"Save Link Account: https://{domain}:81/ssh-{username}.txt\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"✅ Développé par 🜲 PPS TECH.✅\n"
        f" ━━━━━━━━━━━━━━━━━━━━━━━━"
    )

def renew_ssh_account(username, days):
    rc, out, err = _run(f"id {username} 2>/dev/null")
    if rc != 0:
        return False, f"❌ Utilisateur <code>{username}</code> introuvable."
    expiry = (datetime.now() + timedelta(days=days)).strftime("%Y-%m-%d")
    _run(f"chage -E {expiry} {username}")
    return True, f"✅ Compte <code>{username}</code> renouvelé jusqu'au <b>{expiry}</b>."

def delete_ssh_account(username):
    rc, out, err = _run(f"id {username} 2>/dev/null")
    if rc != 0:
        return False, f"❌ Utilisateur <code>{username}</code> introuvable."
    _run(f"pkill -u {username} 2>/dev/null")
    _run(f"userdel -r {username} 2>/dev/null")
    return True, f"✅ Compte <code>{username}</code> supprimé."

def lock_ssh_account(username):
    rc, _, _ = _run(f"id {username} 2>/dev/null")
    if rc != 0:
        return False, f"❌ Utilisateur <code>{username}</code> introuvable."
    _run(f"usermod -L {username}")
    return True, f"🔒 Compte <code>{username}</code> verrouillé."

def unlock_ssh_account(username):
    rc, _, _ = _run(f"id {username} 2>/dev/null")
    if rc != 0:
        return False, f"❌ Utilisateur <code>{username}</code> introuvable."
    _run(f"usermod -U {username}")
    return True, f"🔓 Compte <code>{username}</code> déverrouillé."

def get_ssh_usernames():
    out = subprocess.getoutput(
        "awk -F: '$3>=1000 && $1!=\"nobody\" && $7==\"/bin/false\" {print $1}' /etc/passwd"
    )
    return [u for u in out.splitlines() if u]

def get_ssh_account_details(username):
    rc, _, _ = _run(f"id {username} 2>/dev/null")
    if rc != 0:
        return False, f"❌ Utilisateur <code>{username}</code> introuvable."
    expiry     = subprocess.getoutput(f"chage -l {username} | grep 'Account expires' | cut -d: -f2").strip()
    status_raw = subprocess.getoutput(f"passwd -S {username} 2>/dev/null | awk '{{print $2}}'").strip()
    status     = "🔒 Verrouillé" if status_raw == "L" else "🟢 Actif"
    sessions   = subprocess.getoutput(f"who | grep -c '^{username} ' 2>/dev/null || echo 0").strip()
    return True, (
        f"┏━━━━━━━━━━━━━━━━━━━━━━━━━━┓\n"
        f"┃         DÉTAILS SSH \n"
        f"┗━━━━━━━━━━━━━━━━━━━━━━━━━━┛\n"
        f"👤 Username : <code>{username}</code>\n"
        f"📅 Expiry   : <code>{expiry}</code>\n"
        f"🔐 Statut   : {status}\n"
        f"🔗 Sessions : <b>{sessions}</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"✅ Développé par 🜲 PPS TECH.✅\n"
        f" ━━━━━━━━━━━━━━━━━━━━━━━━"
    )