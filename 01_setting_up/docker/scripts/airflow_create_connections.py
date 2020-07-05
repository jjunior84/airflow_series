import sys, io, json, subprocess, pathlib, os

def build_connection_commands(connection_file_path):
    bash_cmds = []
    file = open(connection_file_path, "r")
    json_connections = json.load(file)
    file.close()

    for connection in json_connections:
        bashCmd = []
        bashCmd.append("airflow")
        bashCmd.append("connections")
        bashCmd.append("-a")
        bashCmd.append("--conn_id=" + str(connection["CONN_ID"]))
        bashCmd.append("--conn_type=" + str(connection["CONN_TYPE"]))
        bashCmd = append_arguments(bashCmd, connection, 'CONN_URI')
        bashCmd = append_arguments(bashCmd, connection, 'CONN_HOST')
        bashCmd = append_arguments(bashCmd, connection, 'CONN_LOGIN')
        bashCmd = append_arguments(bashCmd, connection, 'CONN_PASSWORD')
        bashCmd = append_arguments(bashCmd, connection, 'CONN_SCHEMA')
        bashCmd = append_arguments(bashCmd, connection, 'CONN_PORT')
        bashCmd = append_arguments(bashCmd, connection, 'CONN_EXTRA')

        bash_cmds.append(bashCmd)     

    return bash_cmds       

def append_arguments(bashCmd, connection, argStr):
     if str(connection[argStr]) != "" and str(connection[argStr]) is not None:
            new_arg = ("--" + argStr.lower() + "='" + (str(json.dumps(connection[argStr])) if isinstance(connection[argStr], dict) else str(connection[argStr]).replace("'", '"')) + "'")
            bashCmd.append(new_arg)
     return bashCmd
            
def execute_bash_command(cmd):
    print("Executing: " + ' '.join([str(arg) for arg in cmd]) )
    os.system(' '.join([str(arg) for arg in cmd]))


def main(argv):
   inputfile = argv[0]
   if pathlib.Path(inputfile).name != "connections.json":
       print("connections.json did not find")
       sys.exit()

   cmds = build_connection_commands(inputfile)
   for cmd in cmds:
        execute_bash_command(cmd)

if __name__ == "__main__":
    main(sys.argv[1:])
