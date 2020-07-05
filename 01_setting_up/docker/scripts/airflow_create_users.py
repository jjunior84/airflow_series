import argparse
import sys, io, json, subprocess, pathlib, os

def build_connection_commands(user_file_path, delete_before = False):
    bash_cmds = []
    file = open(user_file_path, "r")
    json_users = json.load(file)
    file.close()
    
    for user in json_users:
        if (delete_before):
            bashCmd = []
            bashCmd.append("airflow")
            bashCmd.append("delete_user")
            bashCmd.append("-u")
            bashCmd.append(str(user))  
            bash_cmds.append(bashCmd)               

        bashCmd = []
        bashCmd.append("airflow")
        bashCmd.append("create_user")
        bashCmd.append("-u")
        bashCmd.append(str(user))
        bashCmd.append("-r")
        bashCmd.append(str(json_users[user]["role"]))       
        bashCmd.append("-e")
        bashCmd.append(str(json_users[user]["email"]))
        bashCmd.append("-f")
        bashCmd.append(str(json_users[user]["firstname"]))
        bashCmd.append("-l")
        bashCmd.append(str(json_users[user]["lastname"]))
        bashCmd.append("-p")
        bashCmd.append(str(json_users[user]["password"]))                               
        bash_cmds.append(bashCmd)     

    return bash_cmds       


def execute_bash_command(cmd):
    print("Executing: " + ' '.join([str(arg) for arg in cmd]) )
    os.system(' '.join([str(arg) for arg in cmd]))


def main(argv):

    if (argv[0] == "-d"):
       delete_before = True
       inputfile = argv[1]
    else:
        delete_before = False
        inputfile = argv[0]

    if pathlib.Path(inputfile).name != "users.json":
       print("users.json did not find")
       sys.exit()

    cmds = build_connection_commands(inputfile, delete_before)
    for cmd in cmds:
        execute_bash_command(cmd)

if __name__ == "__main__":
    main(sys.argv[1:])
