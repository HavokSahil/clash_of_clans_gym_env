import json
import os

def beautify_json(json_str):
    return json.dumps(json.loads(json_str), indent=4)


base_path = f"{os.getcwd()}/jsons"
jsons = os.listdir(base_path)

for item in jsons:
    with open(f"{base_path}/{item}", "r") as file:
        data = file.read()
        # Save the beautified json to the same file
    with open(f"{base_path}/{item}", "w") as file:
        file.write(beautify_json(data))
    print(beautify_json(data))
    print("\n\n\n")