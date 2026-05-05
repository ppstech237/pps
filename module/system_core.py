import subprocess

BRAND = "🜲 PPS"

def get_vps_status():
    cpu    = subprocess.getoutput("top -bn1 | grep 'Cpu(s)' | awk '{print $2+$4\"%\"}'")
    ram    = subprocess.getoutput("free -m | awk 'NR==2{printf \"%s/%sMB (%.0f%%)\", $3,$2,$3*100/$2}'")
    disk   = subprocess.getoutput("df -h / | awk 'NR==2{print $3\"/\"$2\" (\"$5\")\"}'")
    uptime = subprocess.getoutput("uptime -p")
    ip     = subprocess.getoutput("curl -s ifconfig.me").strip()
    domain = subprocess.getoutput("cat /etc/xray/domain 2>/dev/null || echo 'N/A'").strip()

    services = {
        "SSH":     "sshd",
        "Xray":    "xray",
        "Dropbear":"dropbear",
        "WS":      "proxy",
        "ZIVPN":   "zivpn",
        "UDP":     "udp-custom",
    }
    svc_lines = ""
    for name, svc in services.items():
        rc = subprocess.run(f"systemctl is-active {svc} 2>/dev/null", shell=True,
                            capture_output=True, text=True).returncode
        dot = "🟢" if rc == 0 else "🔴"
        svc_lines += f"  {dot} {name}\n"

    return (
        f"┏━━━━━━━━━━━━━━━━━━━━━━━━━━┓\n"
        f"┃         VPS STATUS \n"
        f"┗━━━━━━━━━━━━━━━━━━━━━━━━━━┛\n"
        f"🖥️ IP     : <code>{ip}</code>\n"
        f"🌐 Domain : <code>{domain}</code>\n"
        f"⚙️ CPU    : <b>{cpu}</b>\n"
        f"💾 RAM    : <b>{ram}</b>\n"
        f"💿 Disk   : <b>{disk}</b>\n"
        f"⏱️ Uptime : <b>{uptime}</b>\n\n"
        f"<b>Services :</b>\n{svc_lines}"
    )

def clean_system_logs():
    subprocess.run("journalctl --vacuum-time=1d 2>/dev/null", shell=True)
    subprocess.run("find /var/log -type f -name '*.log' -exec truncate -s 0 {} \\; 2>/dev/null", shell=True)
    subprocess.run("find /var/log -type f -name '*.gz' -delete 2>/dev/null", shell=True)
    return f"✅ <b>Logs système nettoyés ☑️</b>"