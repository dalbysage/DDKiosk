id -u kiosk &>/dev/null || sudo useradd -m kiosk
sudo mkdir -p /var/log/kiosk/
sudo chown kiosk:kiosk /var/log/kiosk/
sudo cp kiosk.py /home/kiosk/
sudo cp kiosk.cfg /home/kiosk/
