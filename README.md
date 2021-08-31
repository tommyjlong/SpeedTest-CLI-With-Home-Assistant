# SpeedTest To Home Assistant
This project provides a way for Home Assistant to run the OKLA official `speedtest.net` binary (binary running on Linux) using an automation.  It consists of the following:
* Home Assistant running its native [Speedtest.net integration](https://www.home-assistant.io/integrations/speedtestdotnet/) in manual mode.
* OKLA [Speedtest-cli binary](https://www.speedtest.net/apps/cli)
* Python Code to launch the Speedtest-cli binary, receive the results, parse them, and post the results to HA using their token based API.
* A Shell script to launch the Python code.
* A Home Assistant automation to call the shell script.

Background - Home Assistant provides a native SpeedTest integration which uses a [third party Python code](https://github.com/sivel/speedtest-cli) to run the actual tests.  The third party code attempts to mimic the official speedtest-cli but the test results of the third party code does not always reflect that of the official speedtest-cli.  

Note: There are other ways for HA to run the Speedtest-CLI binary such as the one provided by the Home Assistant Community Forum [here](https://community.home-assistant.io/t/add-the-official-speedtest-cli/161915/15).

# Instructions
## Home Assistant 
### Home Assistant Speedtest Dot Net
Setup the Speedtest dot net integration in HA and configure the manual mode to TRUE.  Restart HA, and check the Developer's Tools where you should see 3 sensors:
* `sensor.speedtest_download`
* `sensor.speedtest_ping`
* `sensor.speedtest_upload`

Manual mode is required (If you use the GUI check "Disable auto-update").  This prevents the integration from running its own version of speedtest and subsequently prevents it from updating these sensors itself.

Note: HA provides a native service `sensor.update_speedtest` that is used to run the third-party speedtest-cli.  This service is not to be used along with this project.  Instead you will be able to use shell command service called 'launch_speedtest_cli'.

### Home Assistant Token Generation
Follow the instructions for having HA generate a "Long-Lived Access Token".  As of this writting, this is done by going to the User profile and going to the card "Long-Lived Access Token" and clicking "CREATE TOKEN".  A Popup should show you the newly generated token (you can give it some friendly name).  It is required that you copy this token as it will be used later in the python file.

## Setup Your Downloaded Github Files
* Create a directory in you Home Assistant configuration directory, for example named `shell_commands` (which is the default for this project) and copy the `launch_speed_test.sh` and `speedtest-cli-2ha.py` to this directory.  Use a text editor and edit the `speedtest-cli-2ha.py` and fill out the information according to the instructions within this file.  Also, you may need to edit the `launch_speed_test.sh` file to specify the HA config directory path and or Python3 path.

* Goto the OOKLA site mentioned above and get one of the Linux binaries that will run on your system.  You can usually find out by typing in your linux shell: `$uname -m`  which should return something like `x86_64`.  Download that tar file and extract its binary and put it into this same directory (ex. `shell_commands`).  Rename the binary `speedtest.bin`.  If you are running Home Assistant with HassOS, you can do some of this with combinations of the Terminal and SSH add-on and the Samba add-on.

* Accept the Speedtest-CLI EULA. 
  * Method I - Accept the EULA by executing the binary by typing `$ ./speedtest.bin`.  You will get prompted to accept the EULA.  Once accepted, it will store a file away that will allow it to remember this so that next time you won't be prompted again.  It will continue to run and automatically pick a nearby OOKLA server and provide textual results.  The binary is now useable by the python code.
  * Method II - There can be however a problem with this. The file that speedtest.bin writes to after accepting the EULA gets written to the user's home direcotry and  this file may get removed on the next HA upgrade (if using containers) causing the user to have to re-run speedtest.bin by hand in order to accept the EULA.  A preferred alternative is to read the [EULA on-line](https://www.speedtest.net/about/eula) and if the EULA is acceptable, then change the following lines inside the `speedtest-cli-2ha.py` <br/>

From:
```
process = subprocess.Popen([SPEEDTEST_PATH,'--format=json','--precision=4',speed_test_server_id],
```
To:
```
process = subprocess.Popen([SPEEDTEST_PATH,'--format=json','--precision=4', '--accept-license', '--accept-gdpr', speed_test_server_id],
```

## HA Configuration and Automation
* Configure a shell command in your configuration.yaml file:
```
shell_command: #Starting 0.114, command timesout after 60s.
  launch_speedtest_cli: CONFIG-PATH-TO/shell_commands/launch_speed_test.sh
```
This will provide a service called `shell_command.launch_speedtest_cli`.

* Setup the HA automation itself and use the following action:
```
    action:
      - service: shell_command.launch_speedtest_cli
```
## Testing and Debugging
From the GUI goto Developers->Services and select `shell_command.launch_speedtest_cli` and press the button.
After less than a minute, check HA's speedtest sensors to see if they were updated.  

If the sensor did not update, then there may be problems with the file pathnames. To debug this, add the following line to the `launch_speedtest_cli.sh`:
```
echo $SHELL_PATH >> my_test_file
```
include the full path name of my_test_file so you will know where to find it.  Repeat the above test from the developer's service.  Read the contents of the `my_test_file` to see what the pathname is and make corrections to the pathnames in the speedtest-cli-2ha.py (and remove the echo $SHELL_PATH line you added earlier from the launch_speedtest_cli.sh file).
	
If this still doesn't work, then one will need to execute the python code directly. If you are using Home Assistant with HassOS or inside a Docker container, you will have to get inside the homeassistant container itself.

Go into the python file and set the `DEBUG` to 1, and `CONSOLE` to 1, then type `$ ./speedtest-cli-2ha.py`.  This will run the speedtest and provide debug information to get ideas of what the problem is.  

If this works and the sensors are updated, we know the Python code setup is OK.  Next type `$ ./launch_speed_test.sh` and see if there are any problems with it. 
