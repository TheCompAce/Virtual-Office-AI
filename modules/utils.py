import base64
import json
import os

def create_folder_structure(base_folder_path, folder_structure_json):
    """
    Creates a folder structure based on the provided JSON object.
    :param base_folder_path: The path to the base folder where the structure will be created.
    :param folder_structure_json: JSON object representing the folder structure.
    """
    for folder_name, folder_data in folder_structure_json.items():
        # Recursively create subfolders if the item is a folder
        if 'subfolders' in folder_data:
            subfolder_path = os.path.join(base_folder_path, folder_name)
            os.makedirs(subfolder_path, exist_ok=True)
            create_folder_structure(subfolder_path, folder_data['subfolders'])
        # Create files if the item is a file
        elif 'data' in folder_data:
            file_path = os.path.join(base_folder_path, folder_name)
            with open(file_path, 'w') as file:
                file.write(folder_data['data'])
            print(f"Created file: {file_path}")

def folder_to_object(folder_path, exclude="env,.git,.vs,.vscode,__pycache__,task.log"):
    root_obj = {}
    exclude_list = [item.strip() for item in exclude.split(",")]

    for subdir, _, files in os.walk(folder_path):
        # Skip excluded subdirectories
        if any(excluded_item in subdir for excluded_item in exclude_list):
            continue
            
        relative_subdir = os.path.relpath(subdir, folder_path)
        current_dir = root_obj
        if relative_subdir != '.':
            for part in relative_subdir.split(os.sep):
                current_dir = current_dir.setdefault(part, {})

        for file in files:
            # Skip excluded files
            if any(excluded_item in file for excluded_item in exclude_list):
                continue

            file_path = os.path.join(subdir, file)
            try:
                # Try reading the file with UTF-8 encoding
                with open(file_path, 'r', encoding='utf-8') as file_obj:
                    file_data = file_obj.read()
            except UnicodeDecodeError:
                # If UTF-8 decoding fails, read the file as bytes and encode with Base64
                with open(file_path, 'rb') as file_obj:
                    file_data = base64.b64encode(file_obj.read()).decode('utf-8')

            current_dir[file] = {"data": file_data}

    return {"root": root_obj}


def load_options():
    try:
        with open('options.json', 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        return {"api_key": ""}

def save_options(options):
    with open('options.json', 'w') as file:
        json.dump(options, file, indent=2)

def list_companies():
    companies_dir = 'companies'
    company_files = [f for f in os.listdir(companies_dir) if f.endswith('.json')]
    companies = []
    for file in company_files:
        file_path = os.path.join(companies_dir, file)
        with open(file_path, 'r') as f:
            company = json.load(f)
            companies.append((company['name'], file_path))
    return companies


def choose_company():
    companies = list_companies()
    print("\nChoose a Company:")
    for i, (name, _) in enumerate(companies):
        print(f"{i + 1}. {name}")
    choice = int(input("Please choose a company (1-{}): ".format(len(companies)))) - 1
    return companies[choice][1]

def load_company_profile(file_path):
    with open(file_path, 'r') as file:
        company_profile = json.load(file)
    return company_profile
