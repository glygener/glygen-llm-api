import sys
import os
import glob
import json
from optparse import OptionParser
from pathlib import Path
from generate_abstract import GenerateAbstract

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))


def main() -> None:

    usage = "\n%prog  [options]"
    parser = OptionParser(usage,version="%prog version___")
    parser.add_option("-s","--server",action="store",dest="server",help="dev/tst/beta/prd")
    parser.add_option("-p","--prompt",action="store",dest="prompt",help="Enter a valid prompt file.")
    parser.add_option("-j","--json_dir",action="store",dest="json_dir",help="Enter a valid directory with json files.")

    (options,args) = parser.parse_args()

    for key in ([options.server]):
        if not (key):
            parser.print_help()
            sys.exit(0)

    server = options.server

    for key in ([options.prompt]):
        if not (key):
            parser.print_help()
            sys.exit(0)

    prompt = options.prompt

    for key in ([options.json_dir]):
        if not (key):
            parser.print_help()
            sys.exit(0)

    json_dir = options.json_dir

    config_obj = json.loads(open("../../api/config.json", "r").read())

    config_file = config_obj["auth_config"]
    auth_config_obj = json.loads(open(config_file, "r").read())
    LLM_PROVIDER = auth_config_obj[server]["LLM_PROVIDER"]
    LLM_API_KEY = auth_config_obj[server]["LLM_API_KEY"]

    output_dir = os.path.join(
        json_dir, "abstract"
    )
    glob_pattern = os.path.join(json_dir, "*.json")

    files = glob.glob(glob_pattern)
    basenames = {os.path.splitext(os.path.basename(x))[0] for x in files}

    if len(files) != len(basenames):
        print(
            f"Mismatch files ({len(files)}) and base names ({len(basenames)}) lengths."
        )

    os.environ['LLM_PROVIDER'] = LLM_PROVIDER
    os.environ['LLM_API_KEY'] = LLM_API_KEY

    try:
        with open(prompt, 'r') as file:
            content = file.read()
    except FileNotFoundError:
        print(f"Error: The prompt file was not found.")
    except Exception as e:
        print(f"Error: An error occurred while reading prompt file.")

    llm_abstract_client = GenerateAbstract(custom_prompt=content)

    new_output_dir = Path(output_dir)

    try:
        new_output_dir.mkdir(parents=True, exist_ok=True)
    except OSError as e:
        print(f"Error creating output directory: {e}")

    for file in files:
        details_json = json.loads(open(file, "r").read())
        details_str = json.dumps(details_json)
        ai_abstract, search_params_http_code = llm_abstract_client.generate_abstract(input_id="abc", input_json=details_str)
        
        if search_params_http_code == 200:
            file_name = Path(file).stem

            output_file_path = os.path.join(
                new_output_dir, file_name + ".txt"
            )

            try:
                with open(output_file_path, 'w') as file:
                    file.write(ai_abstract)
            except:
                print(f"Error for input file : '{file}'")
        else:
            print(f"Error for input file : '{file}'")


if __name__ == "__main__":
    main()
