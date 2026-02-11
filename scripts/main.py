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

# Localizacion base con la que comparar los archivos que no tienen estructura
TRANSLATED_ONLY_FILES_BASE_LANGUAGE = "es"


"""
Devuelve un diccionario con el contenido de los json leidos

Args:
	dir (str): Directorio del que leer los archivos

Returns:
	dict: Diccionario cuyas claves son las rutas de los json leidos (usando 
		  como raiz STRUCTURE_DIR) y cuyos valores son el contenido de los json 
"""
def load_structure_files(dir = STRUCTURE_DIR):
	structure_files = {}
	if os.path.exists(dir):
		# Se genera el arbol completo del directorio de estructura 
		for root, dirs, files in os.walk(dir):
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
							file_path = file_path.replace(f"{dir}/", "")

							# Se guarda el contenido del json en el diccionario usando la ruta del archivo como key
							structure_files[file_path] = data

					except:
						print(f"{ERROR_COLOR}No se pudo abrir '{file_path}'{NORMAL_COLOR}\n")
						continue
	else:
		print(f"{ERROR_COLOR}'{dir}' no existe{NORMAL_COLOR}")
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
	check_variables (bool): False si solo se quieren comprobar objetos json, 
							True si se quieren comprobar tambien variables

Returns:
	str: texto con todos los errores encontrados para mostrar por consola
"""
def compare_dicts(structure_dict, localized_dict, check_variables = False):
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
		
		# Se obtiene el objeto del archivo de localizacion con la key completa
		localized_value = get_nested_value_from_full_key(full_key, localized_dict)
		
		temp_parent_key = obj_parent_key
		if temp_parent_key == "":
			temp_parent_key = "el objeto raiz"
		error_msg = f"	{ERROR_COLOR}No se encontro localizacion para '{obj_key}' en '{temp_parent_key}'{NORMAL_COLOR} \n"

		# Si el objeto es un diccionario
		if type(structure_value) is dict:
			# Si la key no esta en el archivo de localizacion
			if localized_value is None:
				# Se actualiza la key completa para quitar la actual
				full_key = obj_parent_key

				# Si el objeto no es un nodo de evento o de condicion, falta la localizacion
				if not ("type" in structure_value and (structure_value["type"] == "event" or structure_value["type"] == "condition")):
					errors += error_msg

			# Si lo esta,
			else:
				# Anade una / para las proximas keys (de objetos anidados)
				full_key += "/"

				# Se guardan las keys de todos los objetos anidados al principio de la cola
				for key in structure_value.keys():
					remaining_structure_keys.appendleft(key)
					
		# Si el objeto no es un diccionario
		else:
			# Se actualiza la key completa para quitar la actual
			full_key = obj_parent_key
			
			# Si se estan comprobando tambien los valores de las variables y el valor
			# existe en la estructura, pero no en la localizacion, es que falta
			if check_variables and structure_value is not None and localized_value is None:
				errors += error_msg
	
	return errors



structure_files = load_structure_files()
localization_only_base_files = load_structure_files(f"{MAIN_DIR}/{TRANSLATED_ONLY_FILES_BASE_LANGUAGE}")

# Se borran los archivos que ya estaban en el archivo de estructura
for key in structure_files.keys():
	localization_only_base_files.pop(key)

# Si se han cargado archivos de estructura
if len(structure_files) > 0:
	# Se recorren todos los directorios de localizaciones
	for localization in LOCALIZATION_NAMES:
		localization_folder = f"{MAIN_DIR}/{localization}"
		if os.path.exists(localization_folder):
			print(f"{localization}:")
			# Se genera el arbol completo del directorio de localizacion 
			for root, dirs, files in os.walk(localization_folder):
				# Se recorren todos los archivos del arbol
				for structure_file in files:
					# Si el archivo es un .json
					if structure_file.endswith(".json"):
						# Se obtiene la ruta completa del archivo
						file_path = os.path.join(root, structure_file)

						# Se cambian las \ de la ruta por / y se borra de la ruta la carpeta de localizacion
						file_path = file_path.replace("\\", "/")
						file_path_key = file_path.replace(f"{localization_folder}/", "")

						# Si el archivo existe y se ha guardado previamente en los archivos de estructura o en los de solo localizacion
						if os.path.exists(file_path) and file_path_key in structure_files or file_path_key in localization_only_base_files:
							try:
								with open(file_path, 'r', encoding="utf-8") as json_file:
									# Se carga el archivo de localizacion
									localized_file = json.load(json_file)

									# Se comparan ambos archivos
									if file_path_key in structure_files:
										errors = compare_dicts(structure_files[file_path_key], localized_file)
									else:
										errors = compare_dicts(localization_only_base_files[file_path_key], localized_file, True)

									if (errors != ""):
										print(f"    {FILE_COLOR}{file_path}:{NORMAL_COLOR}")
										print(errors)

							except:
								print(f"    {ERROR_COLOR}No se pudo abrir '{file_path}'{NORMAL_COLOR}\n")
								continue
						else:
							print(f"    {ERROR_COLOR}La localizacion '{localization}' no tiene archivo traducido para '{file_path_key}'{NORMAL_COLOR}\n")	
			print()
		else:
			print(f"{WARNING_COLOR}{localization}: No hay directorio de localizacion{NORMAL_COLOR}\n")