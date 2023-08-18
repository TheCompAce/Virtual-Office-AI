import json
from modules.company_setup import create_company
from modules.flow_menu import setup_company_flow
from modules.bots_menu import setup_company_bots
from modules.utils import load_options, save_options


def main_menu():
    while True:
        print("\nMain Menu:")
        print("1. OpenAI Settings")
        print("2. Setup Company")
        print("3. Setup Company Flow")
        print("4. Setup Company Bots")
        print("5. Execute Company")
        print("6. Exit")
        choice = input("Please choose an option (1-6): ")

        if choice == '1':
            modify_openai_settings()
        elif choice == '2':
            create_company()
        elif choice == '3':
            setup_company_flow()
        elif choice == '4':
            setup_company_bots()
        elif choice == '5':
            print("Execute Company functionality coming soon!")
        elif choice == '6':
            print("Exiting the program...")
            exit()
        else:
            print("Invalid choice. Please enter a number between 1 and 4.")

def modify_openai_settings():
    while True:
        with open('project.json', 'r') as file:
            config = json.load(file)

        openai_settings = config["openai_settings"]
        options = load_options()  # Load options including the API key

        print("\nOpenAI Settings:")
        for key, value in openai_settings.items():
            if key == "models":
                print("Models:")
                for i, model in enumerate(value):
                    print(f"  {i + 1}. Name: {model['name']}, Cost: {model['cost']}")
            else:
                print(f"{key}: {value}")

        print("\nModify OpenAI Settings:")
        print("1. Add Model")
        print("2. Delete Model")
        print("3. Modify API Key")
        print("4. Modify Temperature")
        print("5. Modify Top_p")
        print("6. Modify Max Tokens")
        # print("7. Modify Streaming")  # Commented out as requested
        print("7. Back to Main Menu")
        choice = input("Please choose an option (1-7): ")

        if choice == '1':
            name = input("Enter model name: ")
            cost = float(input("Enter model cost: "))
            type = float(input("Enter model cost: "))
            notes = float(input("Enter model cost: "))
            openai_settings["models"].append({"name": name, "cost": cost, "type": type, "notes": notes})
        elif choice == '2':
            model_index = int(input("Enter the index of the model to delete: ")) - 1
            if 0 <= model_index < len(openai_settings["models"]):
                del openai_settings["models"][model_index]
            else:
                print("Invalid index.")
        elif choice == '3':  # Modify API Key
            new_value = input(f"api_key (current value: {options['api_key']}): ")
            if new_value:
                options["api_key"] = new_value
                save_options(options)  # Save the API key to options.json
        elif choice in ['4', '5', '6']:  # Modify other settings based on choice
            keys = ["api_key", "temperature", "top_p", "max_tokens"]
            key = keys[int(choice) - 3]
            new_value = input(f"{key} (current value: {openai_settings[key]}): ")
            if new_value:
                openai_settings[key] = type(openai_settings[key])(new_value)
        # elif choice == '7':  # Commented out as requested
        #     new_value = input(f"streaming (current value: {openai_settings['streaming']}): ")
        #     if new_value.lower() in ['true', 'false']:
        #         openai_settings['streaming'] = new_value.lower() == 'true'
        elif choice == '7':
            break
        else:
            print("Invalid choice. Please enter a number between 1 and 7.")

        # Save the updated settings to project.json
        config["openai_settings"] = openai_settings
        with open('project.json', 'w') as file:
            json.dump(config, file, indent=2)

        print("Settings updated successfully.")


if __name__ == "__main__":
    main_menu()
