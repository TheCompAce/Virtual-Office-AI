import json
import os
from modules.chat_handler import send_message
from modules.flow_menu import setup_company_flow
from modules.bots_menu import setup_company_bots

def create_company():
    # Ask for a description of the company
    description = input("Please provide a description for the company: ")

    # Ask for the company name (optional)
    name = input("Please provide a name for the company (leave blank for OpenAI to suggest one): ")

    # Ask for the filename to save the company's JSON data (optional)
    filename = input("Please provide a filename to save the company's JSON data (leave blank for OpenAI to suggest one): ")

    # Generate the company structure using OpenAI (including generating name and filename if left blank)
    company_structure = generate_company_structure(description, name, filename)

    # Save the generated company structure to the specified file
    save_company_structure(company_structure)

    # Display the questions and guide the user through the next steps
    company_structure["startup_questions"] = handle_startup_questions(company_structure["startup_questions"])

    save_company_structure(company_structure)

    print("Company setup complete!")

    setup_company_flow()
    setup_company_bots()

def save_company_structure(company_structure):
    if company_structure is None:
        print("Error: Company structure is None.")
        return False
    
    try:
        # Extract the filename from the company_structure
        filename = company_structure.get("filename", "default_company_profile.json")

        # Check if the company_structure is a valid JSON object
        if not isinstance(company_structure, dict):
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

        # Save the company structure to the specified filename
        with open(full_path, 'w') as file:
            json.dump(company_structure, file, indent=2)

        print(f"Company structure saved successfully to {full_path}!")
        return True

    except Exception as e:
        print(f"Error saving company structure: {str(e)}")
        return False

def handle_startup_questions(startup_questions):
    answers = []
    send_to_openai = False

    print("\nStartup Questions:")
    for question in startup_questions:
        print(f"\nQuestion: {question}")
        answer = input("Answer: ")
        if not answer.strip():
            answer = None
            send_to_openai = True
        answers.append({"question": question, "answer": answer})

    if send_to_openai:
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

        # Convert answers to JSON string format
        answers_json_string = json.dumps(answers)

        # Construct the conversation with OpenAI using the system prompt and user input
        conversation = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": answers_json_string}
        ]

        # Send the questions and answers to OpenAI
        openai_response = send_message(conversation, config, selected_model)  # Modify this line to match your OpenAI call

        answers =  openai_response

    return json.loads(answers)


def generate_company_structure(description, name, filename):
    # Read the company prompt file from the project.json configuration
    with open('project.json', 'r') as file:
        config = json.load(file)

    prompt_file = config["prompts"]["company_prompt"]["file"]
    prompt_model = config["prompts"]["company_prompt"]["model"]

    if config["openai_settings"]["base_model"]["use"]:
        prompt_model = config["openai_settings"]["base_model"]["model"]

    # Look for the "gpt-4" model, or default to the first model if not found
    selected_model = next((model for model in config["openai_settings"]["models"] if model["name"] == prompt_model), config["openai_settings"]["models"][0])

    # Read the prompt from the specified file
    with open(prompt_file, 'r') as file:
        system_prompt = file.read()

    # Prepare the user input as a JSON object
    user_input = json.dumps({
        "description": description,
        "name": name,
        "filename": filename
    })

    # Construct the conversation with OpenAI using the system prompt and user input
    conversation = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_input}
    ]

    # Call OpenAI to generate the company structure
    response = send_message(conversation, config, selected_model ) # Function to interact with OpenAI

    # Extract and return the generated company structure from the response
    company_structure = response
    
    return json.loads(company_structure)
