import os
import json
from collections import deque

NORMAL_COLOR = "\033[0;0m"
FILE_COLOR = "\033[96m"
WARNING_COLOR = "\033[93m"
ERROR_COLOR = "\033[91m"

MAIN_DIR = f"../localization"
STRUCTURE_DIR = f"{MAIN_DIR}/structure"
LOCALIZATION_NAMES = [
	"cn-CN", "cn-HK", 
	"en",
	"es", "fr", "pt-BR"
]

def load_structure_files():
	structure_files = {}

	if os.path.exists(STRUCTURE_DIR):
		for root, dirs, files in os.walk(STRUCTURE_DIR):
			for structure_file in files:
				if structure_file.endswith(".json"):
					file_path = os.path.join(root, structure_file)

					with open(file_path, 'r', encoding="utf-8") as json_file:
						data = json.load(json_file)

						file_path = file_path.replace("\\", "/")
						file_path = file_path.replace(f"{STRUCTURE_DIR}/", "")
						structure_files[file_path] = data

	return structure_files


def get_nested_value_from_full_key(full_key, dict):
	keys = full_key.rsplit('/')
	curr_obj = dict
	for key in keys:
		if key in curr_obj:
			curr_obj = curr_obj[key]
		else:
			return None
	return curr_obj


def compare_dicts(structure_dict, localized_dict):
	errors = ""
	remaining_structure_keys = deque(structure_dict.keys())

	full_key = ""
	while(len(remaining_structure_keys) > 0):
		obj_key = remaining_structure_keys.popleft()
		obj_parent_key = full_key
		full_key += f"{obj_key}"

		structure_value = get_nested_value_from_full_key(full_key, structure_dict)
		
		if type(structure_value) is dict:
			localized_value = get_nested_value_from_full_key(full_key, localized_dict)

			if localized_value is None:
				if obj_parent_key == "":
					obj_parent_key = "objeto raiz"
				
				is_event = "type" in structure_value and (structure_value["type"] == "event" or structure_value["type"] == "condition")
				if not is_event:
					errors += f"	{ERROR_COLOR}No se encontro traduccion para '{obj_key}' en '{obj_parent_key}'{NORMAL_COLOR} \n"
				obj_parent_key = ""
				full_key = obj_parent_key
			else:
				full_key += "/"
				for key in structure_value.keys():
					remaining_structure_keys.appendleft(key)
		else:
			full_key = obj_parent_key
	
	return errors


structure_files = load_structure_files()

for localization in LOCALIZATION_NAMES:
    localization_folder = f"{MAIN_DIR}/{localization}"
    print(f"{localization}:")

    if os.path.exists(localization_folder):
        for file_dir, structure_file in structure_files.items():
            file_path = f"{localization_folder}/{file_dir}"
            if os.path.exists(file_path):
                with open(file_path, 'r', encoding="utf-8") as json_file:
                    localized_file = json.load(json_file)
                    errors = compare_dicts(structure_file, localized_file)
                    if (errors != ""):
                        print(f"    {FILE_COLOR}{file_dir}:{NORMAL_COLOR}")
                        print(errors)
                        
            else:
                print(f"La localizacion '{localization}' no tiene archivo traducido para '{file_dir}'")
        print()