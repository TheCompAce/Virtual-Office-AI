import base64
import json
import os
import shutil
import subprocess
from modules.chat_handler import send_message
from modules.utils import create_folder_structure, folder_to_object, list_companies, load_company_profile, choose_company


def edit_bots_menu(company_profile):
    # Check if 'bots' key exists, and if not, initialize it with empty nodes and edges
    if 'bots' not in company_profile:
        company_profile['bots'] = {'bots': [], 'tasks': []}

    while True:
        print("\nEdit Bots Menu:")
        print("1. View Current Bots")
        print("2. Add Bot")
        print("3. Edit Bot")
        print("4. Delete Bot")
        print("5. Add Task")
        print("6. Edit Task")
        print("7. Delete Task")
        print("8. Generate Task Source with OpenAI")
        print("9. Bulk Generate Task Source with OpenAI")
        print("10. Test Task Source.")
        print("11. Generate Bots with OpenAI")
        print("12. Edit Bots with OpenAI Question")
        print("13. Save and Exit")
        choice = input("Please choose an option (1-13): ")

        if choice == '1':
            view_current_bots(company_profile)
        elif choice == '2':
            add_bot(company_profile)
        elif choice == '3':
            edit_bot(company_profile)
        elif choice == '4':
            delete_bot(company_profile)
        elif choice == '5':
            add_task(company_profile)
        elif choice == '6':
            edit_task(company_profile)
        elif choice == '7':
            delete_task(company_profile)
        elif choice == '8':
            company_profile = generate_task_source(company_profile)
        elif choice == '9':
            print("Bulk Generate Task Source with OpenAI. {Code Here}")
        elif choice == '10':
            test_task_source(company_profile)
        elif choice == '11':
            company_profile = generate_bots_with_openai(company_profile)
        elif choice == '12':
            company_profile = question_bots_with_openai(company_profile)
        elif choice == '13':
            save_and_exit(company_profile["company_bots"], company_profile)
            break
        else:
            print("Invalid choice. Please enter a number between 1 and 13.")

def test_task_source(company_profile):
    # Check if 'company_bots' key exists in company_profile, and default to an empty list if not
    company_bots = company_profile.get('company_bots', [])

    if not company_bots:
        print("\nNo bots found. Please add bots before generating source code.")
        return
    
    if not company_profile['company_bots']['tasks']:
        print("\nNo tasks found. Please add tasks before generating source code.")
        return

    print("\nChoose a Task:")
    for i, task in enumerate(company_profile['company_bots']['tasks']):
        print(f"{i + 1}. {task['name']}")
    
    choice = int(input(f"Please choose a task (1-{len(company_profile['company_bots']['tasks'])}): ")) - 1
    chosen_task = company_profile['company_bots']['tasks'][choice]

    if chosen_task['code_folder_path'] is None:
        print("\nSource Code folder path is set to None.")

    # Read the company prompt file from the project.json configuration
    with open('project.json', 'r') as file:
        config = json.load(file)

    prompt_file = config["prompts"]["test_input_prompt"]["file"]
    prompt_model = config["prompts"]["test_input_prompt"]["model"]

    if config["openai_settings"]["base_model"]["use"]:
        prompt_model = config["openai_settings"]["base_model"]["model"]

    # Look for the "gpt-4" model, or default to the first model if not found
    selected_model = next((model for model in config["openai_settings"]["models"] if model["name"] == prompt_model), config["openai_settings"]["models"][0])

    # Read the prompt from the specified file
    with open(prompt_file, 'r') as file:
        system_prompt = file.read()

    # Path to the selected task's folder
    task_folder_path = chosen_task['code_folder_path']

    if (task_folder_path is None):
        print(f"No source for {chosen_task['name']}.")
        return
    
    # Step 1: Reading the task's input prompt from "input_prompt.txt"
    with open(os.path.join(task_folder_path, 'input_prompt.txt'), 'r') as file:
        input_prompt = file.read().strip()
        
    # Step 2: Calling send_message with the test input prompt to create "input.dat"
    # (Placeholder for send_message function call - implementation to be added)
    # Construct the conversation with OpenAI using the system prompt and user input
    conversation = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": input_prompt}
    ]

    # Step 2: Send the questions and answers to OpenAI"
    openai_response = send_message(conversation, config, selected_model)  # Modify this line to match your OpenAI call

    # Writing the generated input file to the task folder
    try:
        file_data = json.loads(openai_response)
        with open(os.path.join(task_folder_path, 'input.dat'), 'w') as file:
            file.write(file_data["input"])

        print(f"Input Data generated correctly.")
        print(f"Starting Task execution ...")
        try:
            # Step 3: Running the "run.bat" file and saving the command's output to "task.log"
            task_log_path = os.path.join(task_folder_path, 'task.log')
            try:
                with open(task_log_path, 'w') as log_file:
                    subprocess.run(['run.bat'], cwd=task_folder_path, stdout=log_file, stderr=log_file)
                
            except:
                print(f"Task execution failed.")

            if os.path.exists(task_log_path):
                with open(task_log_path, 'r') as file:
                    log_data = file.read()

                print(log_data)
                print(f"Command completed successfully.")

                prompt_file = config["prompts"]["code_check_prompt"]["file"]
                prompt_model = config["prompts"]["code_check_prompt"]["model"]

                if config["openai_settings"]["base_model"]["use"]:
                    prompt_model = config["openai_settings"]["base_model"]["model"]

                # Look for the "gpt-4" model, or default to the first model if not found
                selected_model = next((model for model in config["openai_settings"]["models"] if model["name"] == prompt_model), config["openai_settings"]["models"][0])

                # Read the prompt from the specified file
                with open(prompt_file, 'r') as file:
                    system_prompt = file.read()

                # Check if log_data is greater than 1000 characters
                if len(log_data) > 100:
                    # Find the index of the first space character after the 1000th character
                    index = log_data.find(' ', 100)
                    # If a space character is found, slice the string from that index
                    if index != -1:
                        log_data = log_data[index:]
                    # If no space character is found after the 1000th character, slice the last 1000 characters
                    else:
                        log_data = log_data[-100:]

                # Assuming log_data is a string
                log_data_encoded = base64.b64encode(log_data.encode('utf-8')).decode('utf-8')

                try:
                    folder_dump = folder_to_object(task_folder_path)
                    check_data = {
                        "source": folder_dump,
                        "log": log_data_encoded
                    }
                    # 
                    # Step 2: Calling send_message with the test input prompt to create "input.dat"
                    # (Placeholder for send_message function call - implementation to be added)
                    # Construct the conversation with OpenAI using the system prompt and user input
                    check_data = json.dumps(check_data)
                    
                    conversation = [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": check_data}
                    ]
                    
                    try:
                        # Step 2: Send the questions and answers to OpenAI"
                        openai_response = send_message(conversation, config, selected_model)  # Modify this line to match your OpenAI call

                        print(openai_response)
                    except:
                        print(f"Error calling OpenAI {conversation}.")
                except:
                    print(f"Error Reading Log {task_log_path}.")
            else:
                print(f"Unable to find {task_log_path}.")

        except:
            print("Response: " + openai_response)
            print(f"Input Data format failed.")
    except:
        print("Response: " + openai_response)
        print(f"Input Data generation failed.")

    


def generate_task_source(company_profile):
    # Check if 'company_bots' key exists in company_profile, and default to an empty list if not
    company_bots = company_profile.get('company_bots', [])

    if not company_bots:
        print("\nNo bots found. Please add bots before generating source code.")
        return
    
    if not company_profile['company_bots']['tasks']:
        print("\nNo tasks found. Please add tasks before generating source code.")
        return

    print("\nChoose a Task:")
    for i, task in enumerate(company_profile['company_bots']['tasks']):
        print(f"{i + 1}. {task['name']}")
    
    choice = int(input(f"Please choose a task (1-{len(company_profile['company_bots']['tasks'])}): ")) - 1
    chosen_task = company_profile['company_bots']['tasks'][choice]

    if chosen_task['code_folder_path'] is not None:
        print("\nSource code folder already exists for this task.")
        delete_choice = input("Do you want to delete the existing folder and continue? (y/n): ").lower()
        if delete_choice == 'y':
            existing_folder_path = chosen_task['code_folder_path']
            if os.path.exists(existing_folder_path):
                shutil.rmtree(existing_folder_path)
                print(f"Deleted existing folder at {existing_folder_path}")
            chosen_task['code_folder_path'] = None
        else:
            print("Operation canceled.")
            return

    print(f"Description to Use : {chosen_task['description']}")
    explain_more = input("\nDo you want to explain the functionality more? (y/n): ").lower() == 'y'
    functionality_text = input("Please provide additional functionality explanation: ") if explain_more else ""


    # Getting the company's name
    company_name = company_profile['name'].replace(" ", "_")

    # Updating the extract_path to include the company's name
    company_extract_path = os.path.join('companies', company_name)
    os.makedirs(company_extract_path, exist_ok=True)

    # Updating the task_folder_path to be within the company's directory
    task_folder_path = os.path.join(company_extract_path, 'tasks')
    os.makedirs(task_folder_path, exist_ok=True)

    # Creating a folder for the task using its name
    task_folder_name = chosen_task['name'].replace(" ", "_")
    task_folder_path = os.path.join(task_folder_path, task_folder_name)
    os.makedirs(task_folder_path, exist_ok=True)

    # Define the path to the "task_template" folder
    task_template_path = 'task_template'

    # Copy all files and folders from the "task_template" folder to the new task folder
    shutil.copytree(task_template_path, task_folder_path, dirs_exist_ok=True)


    files_str = folder_to_object(task_folder_path)

    task_description_json = {
        "description": chosen_task['description'],
        "functionality": functionality_text,
        "files": files_str
    }

    # Read the company prompt file from the project.json configuration
    with open('project.json', 'r') as file:
        config = json.load(file)

    prompt_file = config["prompts"]["code_create_prompt"]["file"]
    prompt_model = config["prompts"]["code_create_prompt"]["model"]

    if config["openai_settings"]["base_model"]["use"]:
        prompt_model = config["openai_settings"]["base_model"]["model"]

    # Look for the "gpt-4" model, or default to the first model if not found
    selected_model = next((model for model in config["openai_settings"]["models"] if model["name"] == prompt_model), config["openai_settings"]["models"][0])

    # Read the prompt from the specified file
    with open(prompt_file, 'r') as file:
        system_prompt = file.read()

    # Convert the flow to JSON string format
    task_json_string = json.dumps(task_description_json)

    # Construct the conversation with OpenAI using the system prompt and user input
    conversation = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": task_json_string}
    ]

    # Send the questions and answers to OpenAI
    openai_response = send_message(conversation, config, selected_model)  # Modify this line to match your OpenAI call

    # print(openai_response)

    # Writing the generated source code to the task folder
    try:
        create_folder_structure(task_folder_path, json.loads(openai_response)["root"])

        # Update the corresponding task in the company_profile dictionary
        company_profile['company_bots']['tasks'][choice]['code_folder_path'] = task_folder_path
        company_profile['company_bots']['tasks'][choice]['code_status'] = "built"

        print(f"Source code generation completed here {task_folder_path}")
    except:
        print("Response: " + openai_response)
        print(f"Source code generation failed.")    

    return company_profile

def save_and_exit(bots, company_profile):
    while True:
        print("\nDo you want to save the changes to the flow structure?")
        choice = input("Enter 'Y' to save, 'N' to exit without saving: ").strip().lower()

        if choice == 'y':
            # Save the flow structure to the company's JSON file
            filename = company_profile.get("filename", "default_company_profile.json")

            # Check if the company_structure is a valid JSON object
            if not isinstance(company_profile, dict):
                print("Error: Invalid company structure format.")
                return False
            
            # Ensure the filename ends with ".json"
            if not filename.endswith('.json'):
                filename += '.json'

            # Create the "companies" folder if it doesn't exist
            companies_folder = 'companies'
            if not os.path.exists(companies_folder):
                os.makedirs(companies_folder)

            # Full path to save the file
            full_path = os.path.join(companies_folder, filename)
    

            with open(full_path, 'r') as file:
                company_data = json.load(file)

            company_data['company_bots'] = bots
            with open(full_path, 'w') as file:
                json.dump(company_data, file, indent=2)

            print("Flow structure saved successfully.")
            break
        elif choice == 'n':
            print("Exiting without saving changes.")
            break   
        else:
            print("Invalid choice. Please enter 'Y' or 'N'.")


def view_current_bots(company_profile):
    # Check if 'company_bots' key exists in company_profile, and default to an empty list if not
    company_bots = company_profile.get('company_bots', [])

    if not company_bots:
        print("\nNo bots found. Please add bots before generating source code.")
        return
    
    # Display the current flow, including nodes and edges
    print("Company Bots:")
    for node in company_profile['company_bots']['bots']:
        print(f"Id: {node['id']}, Bot: {node['name']}, Description: {node['description']}")
        print(f"\tConnected Nodes:")
        for node_id in node["node_ids"]:
            print(f"\t{node_id}")
        print(f"\tConnected Task:")
        for task_id in node["task_ids"]:
            print(f"\t{task_id}")

    for task in company_profile['company_bots']['tasks']:
        print(f"Id: {task['id']}, Task: {task['name']}, Source Folder : {task.get('code_folder_path', 'null')}, Description: {task['description']}")

def add_bot(company_profile):
    print("\nAdd Bot:")
    bot_id = input("Enter the Id number of the bot: ")
    bot_name = input("Enter the name of the bot: ")
    bot_description = input("Enter the description of the bot: ")
    bot_nodes = input("Enter the linked node ids (list all nodes spearated by a ','): ")
    bot_tasks = input("Enter the linked task ids (list all nodes spearated by a ','): ")

    bot_nodes = bot_nodes.split(',')
    bot_tasks = bot_tasks.split(',')
    
    bot = {
        "id": bot_id,
        "name": bot_name,
        "description": bot_description,
        "node_ids": bot_nodes,
        "task_ids": bot_tasks
    }

    if "company_bots" not in company_profile:
        company_profile["company_bots"] = {"bots": [], "task": []}

    company_profile["company_bots"]["bots"].append(bot)
    print(f"Bot '{bot_name}' added successfully!")

def edit_bot(company_profile):
    print("\nEdit Bot:")
    if "company_bots" not in company_profile or not company_profile["company_bots"]["bots"]:
        print("No bots found. Please add a bot first.")
        return

    for i, bot in enumerate(company_profile["company_bots"]["bots"]):
        print(f"{i + 1}. {bot['name']} - {bot['description']}")

    try:
        selected_index = int(input("Select the bot number you want to edit: ")) - 1
        if selected_index < 0 or selected_index >= len(company_profile["company_bots"]["bots"]):
            print("Invalid selection. Please try again.")
            return

        selected_node = company_profile["company_bots"]["bots"][selected_index]
        print(f"Editing bot: {selected_node['name']}")

        selected_node['id'] = input(f"Enter the new id (current: {selected_node['id']}): ") or selected_node['id']
        selected_node['name'] = input(f"Enter the new name (current: {selected_node['name']}): ") or selected_node['name']
        selected_node['description'] = input(f"Enter the new description (current: {selected_node['description']}): ") or selected_node['description']

        selected_node_ids_input = input(f"Enter the new node Ids (current: {selected_node['node_ids']}, leave blank to clear, separated by ','): ")
        selected_task_ids_input = input(f"Enter the new task Ids (current: {selected_node['task_ids']}, leave blank to clear, separated by ','): ")

        # If the input is not empty, split it by ',' to convert into a list
        selected_node['node_ids'] = selected_node_ids_input.split(',') if selected_node_ids_input else []
        selected_node['task_ids'] = selected_task_ids_input.split(',') if selected_task_ids_input else []


        print(f"Bot '{selected_node['name']}' edited successfully!")
    except ValueError:
        print("Invalid input. Please enter a number.")

def delete_bot(company_profile):
    print("\nDelete Bot:")
    if "copany_bots" not in company_profile or not company_profile["copany_bots"]["bots"]:
        print("No bots found. Please add a bot first.")
        return

    for i, bot in enumerate(company_profile["copany_bots"]["bots"]):
        print(f"{i + 1}. {bot['name']} - {bot['description']}")

    try:
        selected_index = int(input("Select the bot number you want to delete: ")) - 1
        if selected_index < 0 or selected_index >= len(company_profile["copany_bots"]["bots"]):
            print("Invalid selection. Please try again.")
            return

        selected_node = company_profile["copany_bots"]["bots"][selected_index]
        company_profile["copany_bots"]["bots"].pop(selected_index)
        print(f"Bot '{selected_node['name']}' deleted successfully!")

    except ValueError:
        print("Invalid input. Please enter a number.")

def add_task(company_profile):
    print("\nAdd Task:")
    task_id = input("Enter the Id number of the task: ")
    task_name = input("Enter the name of the bot: ")
    task_description = input("Enter the description of the bot: ")
    task_code_file_path = input("Enter the linked code source folder: ")
    if not task_code_file_path:
        task_code_file_path = None
        
    task = {
        "id": task_id,
        "name": task_name,
        "description": task_description,
        "task_code_file_path": task_code_file_path
    }

    if "company_bots" not in company_profile:
        company_profile["company_bots"] = {"bots": [], "tasks": []}

    company_profile["company_bots"]["task"].append(task)
    print(f"Task '{task_name}' added successfully!")

def edit_task(company_profile):
    print("\nEdit Task:")
    if "company_bots" not in company_profile or not company_profile["company_bots"]["tasks"]:
        print("No task found. Please add task first.")
        return

    print("Task:")
    for i, task in enumerate(company_profile["company_bots"]["tasks"]):
        print(f"{i + 1}. From {task['name']} - {task['description']}")

    try:
        task_index = int(input("Select the task number to edit: ")) - 1

        if task_index < 0 or task_index >= len(company_profile["company_bots"]["tasks"]):
            print("Invalid selection. Please try again.")
            return

        selected_task = company_profile["company_bots"]["tasks"][task_index]
        new_id = input(f"Enter the new id for the task (current: {selected_task['id']}): ")
        if new_id:
            selected_task['id'] = new_id

        new_name = input(f"Enter the new name for the task (current: {selected_task['id']}): ")
        if new_name:
            selected_task['name'] = new_name

        new_description = input(f"Enter the new description for the task (current: {selected_task['description']}): ")
        if new_description:
            selected_task['description'] = new_description
        
        task_code_file_path = input(f"Enter the linked code source folder (current: {selected_task['code_folder_path']}): ")
        if not task_code_file_path:
            task_code_file_path = None
        selected_task['code_folder_path'] = task_code_file_path

    except ValueError:
        print("Invalid input. Please enter a number.")

def delete_task(company_profile):
    print("\nDelete Task:")
    if "company_bots" not in company_profile or not company_profile["company_bots"]["tasks"]:
        print("No task found. Please add task first.")
        return

    print("Task:")
    for i, task in enumerate(company_profile["company_bots"]["tasks"]):
        print(f"{i + 1}. From {task['name']} - {task['description']}")

    try:
        task_index = int(input("Select the task number to delete: ")) - 1

        if task_index < 0 or task_index >= len(company_profile["company_bots"]["tasks"]):
            print("Invalid selection. Please try again.")
            return

        confirmation = input(f"Are you sure you want to delete the task {company_profile['company_bots']['tasks']['name']} ? (y/n): ")
        if confirmation.lower() == 'y':
            company_profile["company_bots"]["tasks"].pop(task_index)
            print("Task deleted successfully!")
        else:
            print("Deletion cancelled.")

    except ValueError:
        print("Invalid input. Please enter a number.")


def setup_company_bots():
    print("Setup Company Bots:")
    file_path = choose_company()
    company_profile = load_company_profile(file_path)
    # Proceed to work with the company flow
    print(f"Selected company: {company_profile['name']}")
    edit_bots_menu(company_profile)

def generate_bots_with_openai(company_profile):
    # Check if the flow already exists
    existing_flow = company_profile.get("company_bots", None)
    if existing_flow:
        confirmation = input("Bots structure already exists. Do you want OpenAI to edit the existing bots? (y/n): ")
        if confirmation.lower() != 'y':
            print("Operation cancelled.")
            return company_profile

    # Read the company prompt file from the project.json configuration
    with open('project.json', 'r') as file:
        config = json.load(file)

    prompt_file = config["prompts"]["bots_edit_prompt"]["file"]
    prompt_model = config["prompts"]["bots_edit_prompt"]["model"]

    if config["openai_settings"]["base_model"]["use"]:
        prompt_model = config["openai_settings"]["base_model"]["model"]

    # Look for the "gpt-4" model, or default to the first model if not found
    selected_model = next((model for model in config["openai_settings"]["models"] if model["name"] == prompt_model), config["openai_settings"]["models"][0])

    # Read the prompt from the specified file
    with open(prompt_file, 'r') as file:
        system_prompt = file.read()

    # Convert the flow to JSON string format
    flow_json_string = json.dumps(company_profile)

    # Construct the conversation with OpenAI using the system prompt and user input
    conversation = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": flow_json_string}
    ]

    # Send the questions and answers to OpenAI
    openai_response = send_message(conversation, config, selected_model)  # Modify this line to match your OpenAI call

    # Extract the new flow structure and update the company profile
    new_flow_structure = openai_response

    # Writing the generated source code to the task folder
    try:
        # Assuming new_flow_structure is a JSON string
        new_flow_structure_json = json.loads(new_flow_structure)
        company_profile["company_bots"] = new_flow_structure_json["company_bots"]

        print("Bot structure generated/updated successfully with OpenAI!")
    except:
        print("Response: " + openai_response)
        print(f"Bots structure generation failed.")  

    

    return company_profile

def question_bots_with_openai(company_profile):
    # Check if the flow already exists
    existing_bots = company_profile.get("company_bots", None)
    bots_question = input("Enter a prompt to edit the bots: ")

    # Read the company prompt file from the project.json configuration
    with open('project.json', 'r') as file:
        config = json.load(file)

    prompt_file = config["prompts"]["bots_edit_prompt"]["file"]
    prompt_model = config["prompts"]["bots_edit_prompt"]["model"]

    prompt_question_file = config["prompts"]["bots_question_prompt"]["file"]
    # prompt_question_model = config["prompts"]["bots_question_prompt"]["model"]

    if config["openai_settings"]["base_model"]["use"]:
        prompt_model = config["openai_settings"]["base_model"]["model"]
        # prompt_question_model = prompt_model

    # Look for the "gpt-4" model, or default to the first model if not found
    selected_model = next((model for model in config["openai_settings"]["models"] if model["name"] == prompt_model), config["openai_settings"]["models"][0])

    # Read the prompt from the specified file
    with open(prompt_file, 'r') as file:
        system_prompt = file.read()

    with open(prompt_question_file, 'r') as file:
        system_question_prompt = file.read()

    # Convert the flow to JSON string format
    bots_json_string = json.dumps(company_profile)

    # Construct the conversation with OpenAI using the system prompt and user input
    conversation = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": bots_json_string},
        {"role": "system", "content": system_question_prompt},
        {"role": "user", "content": bots_question}
    ]

    # Send the questions and answers to OpenAI
    openai_response = send_message(conversation, config, selected_model)  # Modify this line to match your OpenAI call

    # Extract the new flow structure and update the company profile
    new_flow_structure = openai_response

    try:
        # Assuming new_flow_structure is a JSON string
        new_flow_structure_json = json.loads(new_flow_structure)
        company_profile["company_bots"] = new_flow_structure_json["company_bots"]

        print("Bots structure generated/updated successfully with OpenAI!")
    except:
        print(new_flow_structure)
        print("Bots structure generated/updated failed with OpenAI!")

    return company_profile

if __name__ == "__main__":
    setup_company_bots()
