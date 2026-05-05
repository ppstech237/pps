#!/bin/bash
# PPS_TECH Telegram Bot Panel - Méthode fiable (systemd)

clear
LN='\e[34m'
BG='\e[44m'
NC='\e[0m'
GR='\e[32m'
RD='\e[31m'

pps_bot_panel() {
    echo -e "${LN}┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓${NC}"
    echo -e "${LN}┃${NC} ${BG}       🜲 PPS_TECH TELEGRAM BOT PANEL           ${NC} ${LN}┃${NC}"
    echo -e "${LN}┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛${NC}"
    echo -e "${LN}┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓${NC}"
    echo -e "${LN}┃${NC}"
    echo -e "${LN}┃${NC} [01] • Install / Configure Telegram Bot"
    echo -e "${LN}┃${NC} [02] • Stop Telegram Bot"
    echo -e "${LN}┃${NC} [03] • Bot Status"
    echo -e "${LN}┃${NC}"
    echo -e "${LN}┃${NC} [00] • Back to Main Menu"
    echo -e "${LN}┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛${NC}"
    echo -e "${LN}●━━━━━━━━━━━━━━━━━━━ 🜲 PPS_TECH ━━━━━━━━━━━━━━━━━━━●${NC}"
    echo ""
    read -p " Select option : " tgopt
    echo ""

    case $tgopt in
        1 | 01)
            mkdir -p /etc/pps_bot

            while true; do
                read -p "Enter your Telegram User ID (numbers only): " TG_USERID
                if [[ "$TG_USERID" =~ ^[0-9]+$ ]] && [ ${#TG_USERID} -ge 6 ]; then
                    break
                else
                    echo -e "${RD}Invalid User ID! Must be numbers only (min 6 digits).${NC}"
                fi
            done

            while true; do
                read -p "Enter your Bot Token: " TG_TOKEN
                if [[ "$TG_TOKEN" =~ ^[0-9]+:[A-Za-z0-9_-]{30,}$ ]]; then
                    break
                else
                    echo -e "${RD}Invalid Token format! Example: 123456:ABCDEF...${NC}"
                fi
            done

            cat > /etc/pps_bot/config.json << EOF
{
    "bot_token": "$TG_TOKEN",
    "super_admin": $TG_USERID
}
EOF

            cat > /etc/systemd/system/ppsbot.service << 'EOF'
[Unit]
Description=PPS Telegram Bot
After=network.target
Wants=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/etc/pps_bot
ExecStart=/usr/bin/python3 -u /etc/pps_bot/ppsbot.py
Restart=always
RestartSec=10
KillMode=process
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF

            if [ ! -f /etc/pps_bot/ppsbot.py ]; then
                echo -e "${RD}⚠️  ppsbot.py not found in /etc/pps_bot/${NC}"
                echo -e "${RD}Downloading it now...${NC}"
                wget -q -O /etc/pps_bot/ppsbot.py "https://raw.githubusercontent.com/ppstech237/pps/main/menu/ppsbot.py"
                chmod +x /etc/pps_bot/ppsbot.py
                if [ ! -f /etc/pps_bot/ppsbot.py ]; then
                    echo -e "${RD}❌ Failed to download ppsbot.py${NC}"
                    read -p "Press Enter to return... "
                    clear
                    pps_bot_panel
                    return
                fi
                echo -e "${GR}✅ ppsbot.py downloaded successfully${NC}"
            fi

            systemctl daemon-reload
            systemctl enable --now ppsbot.service

            echo -e "${GR}✅ Telegram Bot configured and started!${NC}"
            echo -e "${GR}Check status with: systemctl status ppsbot${NC}"
            read -p "Press Enter to return... "
            clear
            menu
            ;;

        2 | 02)
            systemctl stop ppsbot.service 2>/dev/null
            systemctl disable ppsbot.service 2>/dev/null
            echo -e "${GR}✅ Telegram Bot stopped and disabled.${NC}"
            read -p "Press Enter to return... "
            clear
            menu
            ;;

        3 | 03)
            echo -e "${LN}┏━━━━━━━━━━━━━━━━━━━━━━🜲 PPS_TECH.━━━━━━━━━━━━━━━━━━━┓${NC}"
            systemctl status ppsbot.service --no-pager -l
            echo -e "${LN}┗━━━━━━━━━━━━━━━━━━━━━━🜲 PPS_TECH.━━━━━━━━━━━━━━━━━━━┛${NC}"
            read -p "Press Enter to return... "
            clear
            pps_bot_panel
            ;;

        0 | 00)
            clear
            menu
            ;;

        *)
            clear
            pps_bot_panel
            ;;
    esac
}

pps_bot_panel
