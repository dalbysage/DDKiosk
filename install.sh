id -u kiosk &>/dev/null || sudo useradd -m kiosk
id -Gn kiosk | grep gpio &>/dev/null || sudo usermod -G gpio kiosk
sudo mkdir -p /var/log/kiosk/
sudo chown kiosk:kiosk /var/log/kiosk/
sudo cp kiosk.py /home/kiosk/
sudo cp kiosk.cfg /home/kiosk/
