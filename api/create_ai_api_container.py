import os,sys
import string
from optparse import OptionParser
import glob
import json
import subprocess

__version__="1.0"
__status__ = "Dev"


sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

def main() -> None:

    usage = "\n%prog  [options]"
    parser = OptionParser(usage,version="%prog version___")
    parser.add_option("-s","--server",action="store",dest="server",help="dev/tst/beta/prd")
    (options,args) = parser.parse_args()

    for key in ([options.server]):
        if not (key):
            parser.print_help()
            sys.exit(0)

    server = options.server

    config_obj = json.loads(open("./config.json", "r").read())

    ### get config info for docker container creation
    api_image = f"{config_obj['project']}_{server}"
    api_container_name = f"running_{api_image}"
    api_port = config_obj["api_port"][server]
    config_file = config_obj["auth_config"]
    data_path = config_obj["data_path"]
    auth_config_obj = json.loads(open(config_file, "r").read())
    LLM_PROVIDER = auth_config_obj[server]["LLM_PROVIDER"]
    AI_SEARCH_MAX_REQUESTS_PER_HOUR = auth_config_obj[server]["AI_SEARCH_MAX_REQUESTS_PER_HOUR"]
    AI_SEARCH_STATIC_BEARER_TOKEN = auth_config_obj[server]["AI_SEARCH_STATIC_BEARER_TOKEN"]
    LLM_API_KEY = auth_config_obj[server]["LLM_API_KEY"]

    ### create and populate command list
    cmd_list = []

    # command to package the api
    # cmd_list.append("python setup.py bdist_wheel")
    # if no python error, use below line
    cmd_list.append('python3 setup.py bdist_wheel')

    cmd_list.append(f"docker build --no-cache -t {api_image} .")

    # create the command to delete the api container if it already exists
    container_id = (
        subprocess.getoutput(f"docker ps --all | grep {api_container_name}")
        .split(" ")[0]
        .strip()
    )
    if container_id.strip() != "":
        cmd_list.append(f"docker rm -f {container_id}")

    # create the command to create the api docker container
    cmd = f"docker create --name {api_container_name} -p 127.0.0.1:{api_port}:80"
    cmd += f" -e LLM_PROVIDER={LLM_PROVIDER}  -e AI_SEARCH_MAX_REQUESTS_PER_HOUR={AI_SEARCH_MAX_REQUESTS_PER_HOUR}"
    cmd += f" -e AI_SEARCH_STATIC_BEARER_TOKEN={AI_SEARCH_STATIC_BEARER_TOKEN}  -e LLM_API_KEY={LLM_API_KEY}"
    cmd += f" -e DATA_PATH={data_path} -e SERVER={server} -v {data_path}:{data_path} {api_image}"
    cmd_list.append(cmd)

    def run_command(cmd):
        # result = subprocess.run(
        #     cmd,
        #     shell=True,
        #     text=True,
        #     encoding="utf-8",
        #     errors="replace",
        #     capture_output=True,
        # )
        # for python 3.6 and below, use below line
        result = subprocess.run(cmd, shell = True, universal_newlines = True, errors = 'replace', stdout = subprocess.PIPE, stderr = subprocess.PIPE)
        if result.returncode != 0:
            print(
                f"Command failed with error code {result.returncode}: {result.stderr}"
            )
        else:
            print(result.stdout)

    # run the commands
    for cmd in cmd_list:
        run_command(cmd)


if __name__ == "__main__":
    main()
