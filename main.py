import json
from modules.menu import main_menu

# Load project configuration
with open('project.json', 'r') as file:
    config = json.load(file)

# Select a model based on your requirements
# Here, we'll simply use the first model from the array as an example
selected_model = config["openai_settings"]["models"][0]

# Define your conversation logic here
# Example usage
conversation = [
    {"role": "system", "content": "You are a helpful assistant."},
    {"role": "user", "content": "Hello!"}
]

# Call send_message with the selected model
# response = send_message(conversation, config, selected_model)

# Process the response as needed
# print(response)
main_menu()


