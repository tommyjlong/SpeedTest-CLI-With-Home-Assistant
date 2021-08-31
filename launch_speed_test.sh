#!/usr/bin/env python3
import subprocess
process = subprocess.Popen(["python3","./speedtest-cli-2ha.py"],
                           stdout=subprocess.DEVNULL,
                           stderr=subprocess.DEVNULL)
