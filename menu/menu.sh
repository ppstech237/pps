#!/bin/bash
MYIP=$(curl -sS ipv4.icanhazip.com)
readonly SERVER_HOST="https://raw.githubusercontent.com/ppstech237/pps/main"
clear
LN='\e[34m'
BG='\e[44m'
NC='\e[0m'
GR='\e[32m'
RD='\e[31m'
domain=$(cat /etc/xray/domain)
uptime="$(uptime -p | cut -d " " -f 2-10)"
IPV4=$(curl -s -4 ifconfig.co)
IPV6=$(curl -s -6 ifconfig.co)
VERSION_FILE="/etc/version"
INSTALLED_VERSION=$(cat "$VERSION_FILE" 2>/dev/null || echo "0.0")
LATEST_VERSION=$(curl -sS "$SERVER_HOST/version" || echo "$INSTALLED_VERSION")
UPDATE_AVAILABLE=0

version_greater() {
[ "$(printf '%s\n%s\n' "$1" "$2" | sort -V | tail -n1)" = "$1" ] && [ "$1" != "$2" ]
}

if version_greater "$LATEST_VERSION" "$INSTALLED_VERSION"; then
UPDATE_AVAILABLE=1
wget -q -O /usr/local/sbin/update "$SERVER_HOST/menu/update.sh" && chmod +x /usr/local/sbin/update
fi

if [ -f /etc/os-release ]; then
. /etc/os-release
OS="$NAME"
VER="$VERSION_ID"
else
OS=$(uname -s)
VER=$(uname -r)
fi

nginx=$(systemctl is-active nginx)
if [[ $nginx == "active" ]]; then
status_nginx="${GR}RUN${NC}"
else
status_nginx="${RD}OFF${NC}"
fi

xray=$(systemctl is-active xray)
if [[ $xray == "active" ]]; then
status_xray="${GR}RUN${NC}"
else
status_xray="${RD}OFF${NC}"
fi

if systemctl is-active --quiet proxy && systemctl is-active --quiet edu; then
status_ws="${GR}RUN${NC}"
else
status_ws="${RD}OFF${NC}"
fi

confirm_update() {
clear
echo -e "${RD}┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓${NC}"
echo -e "${RD}┃${NC}  Confirm update to v${LATEST_VERSION} ? [y/n]"
echo -e "${RD}┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛${NC}"
read -p "  Choice: " confirm
if [[ "$confirm" == "y" || "$confirm" == "Y" ]]; then
update
else
menu
fi
}

clear
echo -e "${LN}┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓${NC}"
echo -e "${LN}┃${NC} ${BG}             🜲 PPS_TECH TUNNEL                 ${NC} ${LN}┃${NC}"
echo -e "${LN}┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛${NC}"
echo -e "${LN}┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓${NC}"
echo -e "${LN}┃${NC}  OS         : $OS $VER"
echo -e "${LN}┃${NC}  UPTIME     : $uptime"
echo -e "${LN}┃${NC}  IPv4       : ${IPV4:-N/A}"
if [ -n "$IPV6" ]; then
echo -e "${LN}┃${NC}  IPv6       : $IPV6"
fi
echo -e "${LN}┃${NC}  DOMAIN     : $domain"
echo -e "${LN}┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛${NC}"
echo -e "${LN}┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓${NC}"
echo -e "${LN}┃${NC}   NGINX : [$(echo -e ${status_nginx})]    XRAY : [$(echo -e ${status_xray})]    WS : [$(echo -e ${status_ws})]"
echo -e "${LN}┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛${NC}"
echo -e "${LN}┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓${NC}"
echo -e "${LN}┃${NC} ${BG}                       MENU                     ${NC} ${LN}┃${NC}"
echo -e "${LN}┃${NC}"
echo -e "${LN}┃${NC} [01] • SSH/WS MENU        [04] • TROJAN MENU"
echo -e "${LN}┃${NC} [02] • VMESS MENU         [05] • SOCKS MENU"
echo -e "${LN}┃${NC} [03] • VLESS MENU         [06] • ZIVPN MENU"
echo -e "${LN}┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛${NC}"
echo -e "${LN}┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓${NC}"
echo -e "${LN}┃${NC} ${BG}                      TOOLS                     ${NC} ${LN}┃${NC}"
echo -e "${LN}┃${NC}"
echo -e "${LN}┃${NC} [07] • DNS PANEL          [11] • NETGUARD PANEL"
echo -e "${LN}┃${NC} [08] • DOMAIN PANEL       [12] • VPN PORT INFO"
echo -e "${LN}┃${NC} [09] • IPV6 PANEL         [13] • CLEAN VPS LOGS"
echo -e "${LN}┃${NC} [10] • VPS STATUS         [14] • COMMING_SOON.."
echo -e "${LN}┃${NC}"
echo -e "${LN}┃${NC} [15] • ADD TG BOT PANEL"
echo -e "${LN}┃${NC}"
echo -e "${LN}┃${NC} [00] • EXIT               [88] • REBOOT VPS"
echo -e "${LN}┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛${NC}"
echo -e "${LN}●━━━━━━━━━━━━━━━━ 🜲 PPS_TECH ━━━━━━━━━━━━━━━━━●${NC}"

if [ "$UPDATE_AVAILABLE" -eq 1 ]; then
echo -e "${RD}┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓${NC}"
echo -e "${RD}┃${NC} ${RD}[99] • UPDATE SCRIPT (v${LATEST_VERSION})${NC}"
echo -e "${RD}┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛${NC}"
fi

VERSION=$(cat /etc/version)
echo -e "${LN}┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓${NC}"
echo -e "${LN}┃${NC} • VERSION      : ${VERSION}"
echo -e "${LN}┃${NC} • SCRIPT BY    : 🜲 PPS_TECH"
echo -e "${LN}┃${NC} • OUR CONTACT  : +237 690159535"
echo -e "${LN}┃${NC} • OUR CHANNEL  : https://t.me/ppssurf"
echo -e "${LN}┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛${NC}"
echo -e "${LN}●━━━━━━━━━━━━━━━━ 🜲 PPS_TECH ━━━━━━━━━━━━━━━━━●${NC}"
echo ""
read -p " Select menu :  " opt
echo ""

case $opt in
1 | 01) clear ; /usr/local/sbin/ssh ;;
2 | 02) clear ; vmess ;;
3 | 03) clear ; vless ;;
4 | 04) clear ; trojan ;;
5 | 05) clear ; socks ;;
6 | 06) clear ; zivpn ;;
7 | 07) clear ; dns ;;
8 | 08) clear ; domain ;;
9 | 09) clear ; iptools ;;
10) clear ; status ;;
11) clear ; netguard ;;
12) clear ; port ;;
13) clear ; log ;;
14) clear ; echo -e "${RD}This feature is coming soon...${NC}" ; sleep 2 ; menu ;;
15) clear ; pps_bot_panel ;;
88) reboot ;;
99) clear ; confirm_update ;;
0 | 00) exit ;;
*) clear ; menu ;;
esac