import os
import json
from collections import deque

# Colores para los prints (puede no funcionar en cmd)
NORMAL_COLOR = "\033[0;0m"
FILE_COLOR = "\033[96m"
WARNING_COLOR = "\033[93m"
ERROR_COLOR = "\033[91m"


# Ruta padre con todos los archivos de localizacion y estructura
MAIN_DIR = f"../localization"

# Ruta padre de los archivos de estructura
STRUCTURE_DIR = f"{MAIN_DIR}/structure"

# Nombres de las carpetas con los archivos de localizacion
LOCALIZATION_NAMES = [
	"cn-CN", 
	"cn-HK", 
	"en",
	"es", 
	"fr",
	"pt-BR"
]


"""
Devuelve un diccionario con el contenido de los json leidos

Returns:
	dict: Diccionario cuyas claves son las rutas de los json leidos (usando 
		  como raiz STRUCTURE_DIR) y cuyos valores son el contenido de los json 
"""
def load_structure_files():
	structure_files = {}
	if os.path.exists(STRUCTURE_DIR):
		# Se genera el arbol completo del directorio de estructura 
		for root, dirs, files in os.walk(STRUCTURE_DIR):
			# Se recorren todos los archivos del arbol
			for structure_file in files:
				# Si el archivo es un .json
				if structure_file.endswith(".json"):
					# Se obtiene la ruta completa del archivo
					file_path = os.path.join(root, structure_file)
					try:
						with open(file_path, 'r', encoding="utf-8") as json_file:
							# Se carga el json
							data = json.load(json_file)

							# Se cambian las \ de la ruta por / y se borra de la ruta la carpeta de localizacion
							file_path = file_path.replace("\\", "/")
							file_path = file_path.replace(f"{STRUCTURE_DIR}/", "")

							# Se guarda el contenido del json en el diccionario usando la ruta del archivo como key
							structure_files[file_path] = data

					except:
						print(f"{ERROR_COLOR}No se pudo abrir '{file_path}'{NORMAL_COLOR}\n")
						continue
	else:
		print(f"{ERROR_COLOR}'{STRUCTURE_DIR}' no existe{NORMAL_COLOR}")
	return structure_files


"""
Devuelve el objeto del diccionario correspondiente a la key indicada

Args:
	full_key (str): Key del objeto del diccionario. Se pueden buscar objetos anidado
					dentro de otros pasando una key del tipo objeto1/objeto2/...
	dict (dict): Diccionario en el que buscar el objeto

Returns:
	Any: Objeto correspondiente a la key. Si no existe, se devuelve None
"""
def get_nested_value_from_full_key(full_key, dict):
	# Se obtienen las keys de todos los objetos
	keys = full_key.rsplit('/')
	
	# El objeto actual en el que buscar es el diccionario
	curr_obj = dict
	
	# Se recorren todas las keys
	for key in keys:
		# Si la key esta en el objeto en el que buscar, la siguiente key se buscara en el objeto encontrado
		if key in curr_obj:
			curr_obj = curr_obj[key]
		# Si no, se detiene la busqueda
		else:
			return None
	return curr_obj


"""
Se comparan los nodos del archivo de estructura con los nodos del archivo de localizacion 

Args:
	structure_dict (str): json del archivo de estructura
	localized_dict (dict): json del archivo de localizacion

Returns:
	str: texto con todos los errores encontrados para mostrar por consola
"""
def compare_dicts(structure_dict, localized_dict):
	errors = ""

	# Se guardan todas las keys del objeto raiz del archivo de estructura
	remaining_structure_keys = deque(structure_dict.keys())

	# key completa del objeto actual
	full_key = ""

	# Se van recorriendo las keys hasta que ya no haya mas 
	while(len(remaining_structure_keys) > 0):
		# Se saca la primera key de la cola
		obj_key = remaining_structure_keys.popleft()

		# Se guarda la key del objeto en el que esta la key actual
		obj_parent_key = full_key

		# Se actualiza la key completa para incluir la actual
		full_key += f"{obj_key}"

		# Se obtiene el objeto del archivo de estructura con la key completa
		structure_value = get_nested_value_from_full_key(full_key, structure_dict)
		
		# Si el objeto es un diccionario
		if type(structure_value) is dict:
			# Se obtiene el objeto del archivo de localizacion con la key completa
			localized_value = get_nested_value_from_full_key(full_key, localized_dict)

			# Si la key no esta en el archivo de localizacion
			if localized_value is None:
				temp_parent_key = obj_parent_key
				if temp_parent_key == "":
					temp_parent_key = "el objeto raiz"
				
				if not ("type" in structure_value and (structure_value["type"] == "event" or structure_value["type"] == "condition")):
					errors += f"	{ERROR_COLOR}No se encontro traduccion para '{obj_key}' en '{temp_parent_key}'{NORMAL_COLOR} \n"

				# Se actualiza la key completa para quitar la actual
				full_key = obj_parent_key
			# Si lo esta,
			else:
				# Anade una / para las proximas keys (de objetos anidados)
				full_key += "/"

				# Se guardan las keys de todos los objetos anidados al principio de la cola
				for key in structure_value.keys():
					remaining_structure_keys.appendleft(key)
					
		# Si el objeto no es un diccionario, se actualiza la key completa para quitar la actual
		else:
			full_key = obj_parent_key
	
	return errors



structure_files = load_structure_files()

# Si se han cargado archivos de estructura
if len(structure_files) > 0:
	# Se recorren todos los directorios de localizaciones
	for localization in LOCALIZATION_NAMES:
		localization_folder = f"{MAIN_DIR}/{localization}"
		if os.path.exists(localization_folder):
			print(f"{localization}:")

			# Se recorren todos los json leidos
			for file_dir, structure_file in structure_files.items():
				# Se obtiene la ruta del archivo en el directorio de localizacion correspondiente
				file_path = f"{localization_folder}/{file_dir}"
				if os.path.exists(file_path):
					try:
						with open(file_path, 'r', encoding="utf-8") as json_file:
							# Se carga el archivo de localizacion
							localized_file = json.load(json_file)

							# Se comparan ambos archivos
							errors = compare_dicts(structure_file, localized_file)
							if (errors != ""):
								print(f"    {FILE_COLOR}{file_dir}:{NORMAL_COLOR}")
								print(errors)
					except:
						print(f"    {ERROR_COLOR}No se pudo abrir '{file_path}'{NORMAL_COLOR}\n")
						continue
				else:
					print(f"    {ERROR_COLOR}La localizacion '{localization}' no tiene archivo traducido para '{file_dir}'{NORMAL_COLOR}\n")
			print()
		else:
			print(f"{WARNING_COLOR}{localization}: No hay directorio de localizacion{NORMAL_COLOR}\n")
