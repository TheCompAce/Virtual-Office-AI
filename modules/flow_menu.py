import json
import os
from modules.chat_handler import send_message

base_model = "gpt-3.5-turbo"

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

def edit_flow_menu(company_profile):
    # Check if 'flow' key exists, and if not, initialize it with empty nodes and edges
    if 'flow' not in company_profile:
        company_profile['flow'] = {'nodes': [], 'edges': []}

    while True:
        print("\nEdit Flow Menu:")
        print("1. View Current Flow")
        print("2. Add Node")
        print("3. Edit Node")
        print("4. Delete Node")
        print("5. Add Edge (Connection)")
        print("6. Edit Edge (Connection)")
        print("7. Delete Edge (Connection)")
        print("8. Generate Flow with OpenAI")
        print("9. Edit Flow with OpenAI Question")
        print("10. Save and Exit")
        choice = input("Please choose an option (1-10): ")

        if choice == '1':
            view_current_flow(company_profile)
        elif choice == '2':
            add_node(company_profile)
        elif choice == '3':
            edit_node(company_profile)
        elif choice == '4':
            delete_node(company_profile)
        elif choice == '5':
            add_edge(company_profile)
        elif choice == '6':
            edit_edge(company_profile)
        elif choice == '7':
            delete_edge(company_profile)
        elif choice == '8':
            company_profile = generate_flow_with_openai(company_profile)
        elif choice == '9':
            company_profile = question_flow_with_openai(company_profile)
        elif choice == '10':
            save_and_exit(company_profile["flow"], company_profile)
            break
        else:
            print("Invalid choice. Please enter a number between 1 and 9.")

def save_and_exit(flow, company_profile):
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

            company_data['flow'] = flow
            with open(full_path, 'w') as file:
                json.dump(company_data, file, indent=2)

            print("Flow structure saved successfully.")
            break
        elif choice == 'n':
            print("Exiting without saving changes.")
            break   
        else:
            print("Invalid choice. Please enter 'Y' or 'N'.")


def view_current_flow(company_profile):
    # Display the current flow, including nodes and edges
    print("Company Flow:")
    for node in company_profile['flow']['nodes']:
        print(f"Id: {node['id']}, Node: {node['name']}, Type: {node['type']}, Assigned To: {node['assigned_to']}, Description: {node['description']}")
    for edge in company_profile['flow']['edges']:
        print(f"Connection from {edge['from']} to {edge['to']}: {edge['description']}")

def add_node(company_profile):
    print("\nAdd Node:")
    node_id = input("Enter the Id number of the node (task or component): ")
    node_name = input("Enter the name of the node (task or component): ")
    node_description = input("Enter the description of the node: ")
    node_type = input("Enter the type of the node (e.g., task, department, etc.): ")
    assigned_to = input("Enter who or what is assigned to this node (e.g., department name, employee role): ")
    
    node = {
        "id": node_id,
        "name": node_name,
        "description": node_description,
        "type": node_type,
        "assigned_to": assigned_to
    }

    if "flow" not in company_profile:
        company_profile["flow"] = {"nodes": [], "edges": []}

    company_profile["flow"]["nodes"].append(node)
    print(f"Node '{node_name}' added successfully!")

def edit_node(company_profile):
    print("\nEdit Node:")
    if "flow" not in company_profile or not company_profile["flow"]["nodes"]:
        print("No nodes found. Please add a node first.")
        return

    for i, node in enumerate(company_profile["flow"]["nodes"]):
        print(f"{i + 1}. {node['name']} - {node['description']}")

    try:
        selected_index = int(input("Select the node number you want to edit: ")) - 1
        if selected_index < 0 or selected_index >= len(company_profile["flow"]["nodes"]):
            print("Invalid selection. Please try again.")
            return

        selected_node = company_profile["flow"]["nodes"][selected_index]
        print(f"Editing node: {selected_node['name']}")

        selected_node['id'] = input(f"Enter the new id (current: {selected_node['id']}): ") or selected_node['id']
        selected_node['name'] = input(f"Enter the new name (current: {selected_node['name']}): ") or selected_node['name']
        selected_node['description'] = input(f"Enter the new description (current: {selected_node['description']}): ") or selected_node['description']
        selected_node['type'] = input(f"Enter the new type (current: {selected_node['type']}): ") or selected_node['type']
        selected_node['assigned_to'] = input(f"Enter the new assigned entity (current: {selected_node['assigned_to']}): ") or selected_node['assigned_to']

        print(f"Node '{selected_node['name']}' edited successfully!")
    except ValueError:
        print("Invalid input. Please enter a number.")

def delete_node(company_profile):
    print("\nDelete Node:")
    if "flow" not in company_profile or not company_profile["flow"]["nodes"]:
        print("No nodes found. Please add a node first.")
        return

    for i, node in enumerate(company_profile["flow"]["nodes"]):
        print(f"{i + 1}. {node['name']} - {node['description']}")

    try:
        selected_index = int(input("Select the node number you want to delete: ")) - 1
        if selected_index < 0 or selected_index >= len(company_profile["flow"]["nodes"]):
            print("Invalid selection. Please try again.")
            return

        selected_node = company_profile["flow"]["nodes"][selected_index]
        company_profile["flow"]["nodes"].pop(selected_index)
        print(f"Node '{selected_node['name']}' deleted successfully!")

        # Deleting corresponding edges if any
        company_profile["flow"]["edges"] = [edge for edge in company_profile["flow"]["edges"] if edge["from"] != selected_node["name"] and edge["to"] != selected_node["name"]]

    except ValueError:
        print("Invalid input. Please enter a number.")

def add_edge(company_profile):
    print("\nAdd Edge:")
    if "flow" not in company_profile or not company_profile["flow"]["nodes"]:
        print("No nodes found. Please add nodes first.")
        return

    print("Nodes:")
    for i, node in enumerate(company_profile["flow"]["nodes"]):
        print(f"{i + 1}. {node['name']} - {node['description']}")

    try:
        from_node_index = int(input("Select the source node number: ")) - 1
        to_node_index = int(input("Select the destination node number: ")) - 1

        if from_node_index < 0 or from_node_index >= len(company_profile["flow"]["nodes"]) or \
           to_node_index < 0 or to_node_index >= len(company_profile["flow"]["nodes"]) or \
           from_node_index == to_node_index:
            print("Invalid selection. Please try again.")
            return

        from_node = company_profile["flow"]["nodes"][from_node_index]['name']
        to_node = company_profile["flow"]["nodes"][to_node_index]['name']
        description = input("Enter the description for the edge: ")

        if "edges" not in company_profile["flow"]:
            company_profile["flow"]["edges"] = []

        company_profile["flow"]["edges"].append({
            "from": from_node,
            "to": to_node,
            "description": description
        })
        print(f"Edge from '{from_node}' to '{to_node}' added successfully!")

    except ValueError:
        print("Invalid input. Please enter a number.")

def edit_edge(company_profile):
    print("\nEdit Edge:")
    if "flow" not in company_profile or not company_profile["flow"]["edges"]:
        print("No edges found. Please add edges first.")
        return

    print("Edges:")
    for i, edge in enumerate(company_profile["flow"]["edges"]):
        print(f"{i + 1}. From {edge['from']} to {edge['to']} - {edge['description']}")

    try:
        edge_index = int(input("Select the edge number to edit: ")) - 1

        if edge_index < 0 or edge_index >= len(company_profile["flow"]["edges"]):
            print("Invalid selection. Please try again.")
            return

        selected_edge = company_profile["flow"]["edges"][edge_index]
        new_description = input(f"Enter the new description for the edge (current: {selected_edge['description']}): ")
        if new_description:
            selected_edge['description'] = new_description
            print("Edge updated successfully!")

    except ValueError:
        print("Invalid input. Please enter a number.")

def delete_edge(company_profile):
    print("\nDelete Edge:")
    if "flow" not in company_profile or not company_profile["flow"]["edges"]:
        print("No edges found. Please add edges first.")
        return

    print("Edges:")
    for i, edge in enumerate(company_profile["flow"]["edges"]):
        print(f"{i + 1}. From {edge['from']} to {edge['to']} - {edge['description']}")

    try:
        edge_index = int(input("Select the edge number to delete: ")) - 1

        if edge_index < 0 or edge_index >= len(company_profile["flow"]["edges"]):
            print("Invalid selection. Please try again.")
            return

        confirmation = input(f"Are you sure you want to delete the edge from {company_profile['flow']['edges'][edge_index]['from']} to {company_profile['flow']['edges'][edge_index]['to']}? (y/n): ")
        if confirmation.lower() == 'y':
            company_profile["flow"]["edges"].pop(edge_index)
            print("Edge deleted successfully!")
        else:
            print("Deletion cancelled.")

    except ValueError:
        print("Invalid input. Please enter a number.")


def setup_company_flow():
    print("Setup Company Flow:")
    file_path = choose_company()
    company_profile = load_company_profile(file_path)
    # Proceed to work with the company flow
    print(f"Selected company: {company_profile['name']}")
    edit_flow_menu(company_profile)

def generate_flow_with_openai(company_profile):
    # Check if the flow already exists
    existing_flow = company_profile.get("flow", None)
    if existing_flow:
        confirmation = input("Flow structure already exists. Do you want OpenAI to edit the existing flow? (y/n): ")
        if confirmation.lower() != 'y':
            print("Operation cancelled.")
            return company_profile

    # Read the company prompt file from the project.json configuration
    with open('project.json', 'r') as file:
        config = json.load(file)

    # Look for the "gpt-4" model, or default to the first model if not found
    selected_model = next((model for model in config["openai_settings"]["models"] if model["name"] == base_model), config["openai_settings"]["models"][0])

    # Load the prompt from the file
    with open('prompts/flow_edit_prompt.txt', 'r') as file:
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

    # Assuming new_flow_structure is a JSON string
    new_flow_structure_json = json.loads(new_flow_structure)
    company_profile["flow"] = new_flow_structure_json["flow"]

    print("Flow structure generated/updated successfully with OpenAI!")

    return company_profile

def question_flow_with_openai(company_profile):
    # Check if the flow already exists
    existing_flow = company_profile.get("flow", None)
    flow_question = input("Enter a prompt to edit the flow: ")

    # Read the company prompt file from the project.json configuration
    with open('project.json', 'r') as file:
        config = json.load(file)

    # Look for the "gpt-4" model, or default to the first model if not found
    selected_model = next((model for model in config["openai_settings"]["models"] if model["name"] == base_model), config["openai_settings"]["models"][0])

    # Load the prompt from the file
    with open('prompts/flow_edit_prompt.txt', 'r') as file:
        system_prompt = file.read()

    with open('prompts/flow_question_prompt.txt', 'r') as file:
        system_question_prompt = file.read()

    # Convert the flow to JSON string format
    flow_json_string = json.dumps(company_profile)

    # Construct the conversation with OpenAI using the system prompt and user input
    conversation = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": flow_json_string},
        {"role": "system", "content": system_question_prompt},
        {"role": "user", "content": flow_question}
    ]

    # Send the questions and answers to OpenAI
    openai_response = send_message(conversation, config, selected_model)  # Modify this line to match your OpenAI call

    # Extract the new flow structure and update the company profile
    new_flow_structure = openai_response

    # Assuming new_flow_structure is a JSON string
    new_flow_structure_json = json.loads(new_flow_structure)
    company_profile["flow"] = new_flow_structure_json["flow"]

    print("Flow structure generated/updated successfully with OpenAI!")

    return company_profile

if __name__ == "__main__":
    setup_company_flow()
