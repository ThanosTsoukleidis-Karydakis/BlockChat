# runner.py

# Import the necessary modules
import subprocess
import time

# Define the paths to your scripts
script1_path = "./User1.py"
script2_path = "./User1Proxy.py"



# Run the scripts one by one in the desired order, opening a new terminal for each
subprocess.Popen(["gnome-terminal", "--", "python3", script1_path])
subprocess.Popen(["gnome-terminal", "--", "python3", script2_path])

script1_path = "./User2.py"
script2_path = "./User2Proxy.py"

time.sleep(4)

# Run the scripts one by one in the desired order, opening a new terminal for each
subprocess.Popen(["gnome-terminal", "--", "python3", script1_path])
subprocess.Popen(["gnome-terminal", "--", "python3", script2_path])

script1_path = "./User3.py"
script2_path = "./User3Proxy.py"

time.sleep(4)

# Run the scripts one by one in the desired order, opening a new terminal for each
subprocess.Popen(["gnome-terminal", "--", "python3", script1_path])
subprocess.Popen(["gnome-terminal", "--", "python3", script2_path])

script1_path = "./User4.py"
script2_path = "./User4Proxy.py"

time.sleep(4)

# Run the scripts one by one in the desired order, opening a new terminal for each
subprocess.Popen(["gnome-terminal", "--", "python3", script1_path])
subprocess.Popen(["gnome-terminal", "--", "python3", script2_path])

script1_path = "./User5.py"
script2_path = "./User5Proxy.py"

time.sleep(4)

# Run the scripts one by one in the desired order, opening a new terminal for each
subprocess.Popen(["gnome-terminal", "--", "python3", script1_path])
subprocess.Popen(["gnome-terminal", "--", "python3", script2_path])

# script1_path = "./User6.py"
# script2_path = "./User6Proxy.py"

# time.sleep(4)

# # Run the scripts one by one in the desired order, opening a new terminal for each
# subprocess.Popen(["gnome-terminal", "--", "python3", script1_path])
# subprocess.Popen(["gnome-terminal", "--", "python3", script2_path])

# script1_path = "./User7.py"
# script2_path = "./User7Proxy.py"

# time.sleep(4)

# # Run the scripts one by one in the desired order, opening a new terminal for each
# subprocess.Popen(["gnome-terminal", "--", "python3", script1_path])
# subprocess.Popen(["gnome-terminal", "--", "python3", script2_path])

# script1_path = "./User8.py"
# script2_path = "./User8Proxy.py"

# time.sleep(5)

# # Run the scripts one by one in the desired order, opening a new terminal for each
# subprocess.Popen(["gnome-terminal", "--", "python3", script1_path])
# subprocess.Popen(["gnome-terminal", "--", "python3", script2_path])

# script1_path = "./User9.py"
# script2_path = "./User9Proxy.py"

# time.sleep(5)

# # Run the scripts one by one in the desired order, opening a new terminal for each
# subprocess.Popen(["gnome-terminal", "--", "python3", script1_path])
# subprocess.Popen(["gnome-terminal", "--", "python3", script2_path])

# script1_path = "./User10.py"
# script2_path = "./User10Proxy.py"

# time.sleep(5)

# # Run the scripts one by one in the desired order, opening a new terminal for each
# subprocess.Popen(["gnome-terminal", "--", "python3", script1_path])
# subprocess.Popen(["gnome-terminal", "--", "python3", script2_path])


time.sleep(7)
script1_path = "./cli1.py"
# script2_path = "./cli2.py"
script3_path = "./cli3.py"
# script4_path = "./cli4.py"
# script5_path = "./cli5.py"
# script6_path = "./cli6.py"
# script7_path = "./cli7.py"
# script8_path = "./cli8.py"
# script9_path = "./cli9.py"
# script10_path = "./cli10.py"
subprocess.Popen(["gnome-terminal", "--", "python3", script1_path])
# subprocess.Popen(["gnome-terminal", "--", "python3", script2_path])
subprocess.Popen(["gnome-terminal", "--", "python3", script3_path])
# subprocess.Popen(["gnome-terminal", "--", "python3", script4_path])
# subprocess.Popen(["gnome-terminal", "--", "python3", script5_path])

# subprocess.Popen(["gnome-terminal", "--", "python3", script6_path])
# subprocess.Popen(["gnome-terminal", "--", "python3", script7_path])
# subprocess.Popen(["gnome-terminal", "--", "python3", script8_path])
# subprocess.Popen(["gnome-terminal", "--", "python3", script9_path])
# subprocess.Popen(["gnome-terminal", "--", "python3", script10_path])
