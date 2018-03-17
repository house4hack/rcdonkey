RC Donkey
====

Based on the excellent project by Will Roscoe [https://github.com/wroscoe/donkey]

Simplified to use RC during training and driving - removing the need for WiFi and control using smartphone.

Talk from SatRDay included as a branch.


To automate running donkeyreader:

```
---------------------------------------------------

pi@raspberrypi:~ $ cat /etc/init.d/run_ai.sh
#!/bin/bash
### BEGIN INIT INFO
# Provides:          sample.py
# Required-Start:    $remote_fs $syslog
# Required-Stop:     $remote_fs $syslog
# Default-Start:     2 3 4 5
# Default-Stop:      0 1 6
# Short-Description: Start daemon at boot time
# Description:       Enable service provided by daemon.
### END INIT INFO

cd /home/pi/rcdonkey/donkeyreader/
./run.sh
pi@raspberrypi:~ $

pi@raspberrypi:~ $ sudo chmod +x /etc/init.d/run_ai.sh
pi@raspberrypi:~ $ sudo update-rc.d run_ai.sh defaults
pi@raspberrypi:~ $ sudo reboot

Done, once your Raspi booted up run.sh (donkeyreader) should already run in the background
---------------------------------------------------
```
