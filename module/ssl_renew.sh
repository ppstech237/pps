renew_ssl() {
systemctl stop xray
systemctl stop nginxp
"/root/.acme.sh"/acme.sh --cron --home "/root/.acme.sh" &> /root/renew_ssl.log
systemctl start nginx
systemctl start xray
}
