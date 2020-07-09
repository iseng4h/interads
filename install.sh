mkdir csv
mkdir record

sudo apt-get install libbluetooth-dev

pip install PyBluez
pip install paho-mqtt

cd ~/interads

sudo cp active-time.service /etc/systemd/system
sudo cp active-time-user.service /etc/systemd/user
sudo cp count.service /etc/systemd/user
sudo cp mqtt-handler.service /etc/systemd/system
sudo cp rebooter.service /etc/systemd/system
sudo cp resetter.service /etc/systemd/system
sudo cp scanner.service /etc/systemd/system
sudo cp scanner.timer /etc/systemd/system
sudo cp sender.service /etc/systemd/system
sudo cp sender.timer /etc/systemd/system

sudo systemctl daemon-reload
systemctl --user daemon-reload

sudo systemctl enable active-time
systemctl --user enable active-time-user
systemctl --user enable count
sudo systemctl enable mqtt-handler
sudo systemctl enable rebooter
sudo systemctl enable resetter
sudo systemctl enable scanner.timer
sudo systemctl enable sender.timer

chmod +x *.sh
chmod +x *.py
