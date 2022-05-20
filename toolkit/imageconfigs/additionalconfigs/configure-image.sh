echo Enabling service for Azure Serial Console
systemctl enable serial-getty@ttyS0.service
if [[ -f "/etc/systemd/network/99-dhcp-en.network" ]]; then
    echo Removing contents of 99-dhcp-en.network file
    truncate -s 0 /etc/systemd/network/99-dhcp-en.network
fi
