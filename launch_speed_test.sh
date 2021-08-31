#CONFIG_PATH: Full path name where your homeassistant config directory is at
#Python3: Uses "env" to search PATH variable to find location of python3.
CONFIG_PATH=/config
SHELL_PATH=$CONFIG_PATH/shell_commands
/usr/bin/env python3 $SHELL_PATH/speedtest-cli-2ha.py $SHELL_PATH &

