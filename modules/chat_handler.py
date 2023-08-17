import requests
import torch
from transformers import LlamaForCausalLM, LlamaTokenizer, AutoModelForCausalLM, AutoTokenizer, pipeline
from modules.utils import load_options

def send_message(conversation, config, model):  # Add model as a parameter

    if (model["name"] == "psmathur/orca_mini_7b" or model["name"] == "garage-bAInd/Platypus2-13B"):
        # Hugging Face model_path
        model_path = model["name"]
        tokenizer = LlamaTokenizer.from_pretrained(model_path, use_auth_token=True)
        model = LlamaForCausalLM.from_pretrained(
            model_path, torch_dtype=torch.float32, offload_folder="offload"
        )

        system_prompts = [entry['content'] for entry in conversation if entry['role'] == 'system']
        user_inputs = [entry['content'] for entry in conversation if entry['role'] == 'user']

        prompt = ""
        for system_prompt, user_input in zip(system_prompts, user_inputs):
            prompt += f"### System: {system_prompt}### User: {user_input}\n\n### Assistant:\n"
        
        tokens = tokenizer.encode(prompt)
        tokens = torch.LongTensor(tokens).unsqueeze(0)

        instance = {'input_ids': tokens, 'top_p': 1.0, 'temperature': 0.7, 'generate_len': 1024, 'top_k': 50}

        length = len(tokens[0])
        with torch.no_grad():
            rest = model.generate(
                input_ids=tokens,
                max_length=length + instance['generate_len'],
                use_cache=True,
                do_sample=True,
                top_p=instance['top_p'],
                temperature=instance['temperature'],
                top_k=instance['top_k']
            )
        output = rest[0][length:]
        string = tokenizer.decode(output, skip_special_tokens=True)

        print(string)

        return string
    elif (model["name"] == "stabilityai/StableBeluga2" or model["name"] == "The-Face-Of-Goonery/Huginn-13b-FP16" or model["name"] == "circulus/Llama-2-7b-orca-v1"):
        tokenizer = AutoTokenizer.from_pretrained(model["name"], use_fast=False)
        model = AutoModelForCausalLM.from_pretrained(model["name"], offload_folder="offload", torch_dtype=torch.float16, low_cpu_mem_usage=True, device_map="auto")
        
        system_prompts = [entry['content'] for entry in conversation if entry['role'] == 'system']
        user_inputs = [entry['content'] for entry in conversation if entry['role'] == 'user']

        prompt = ""
        for system_prompt, user_input in zip(system_prompts, user_inputs):
            prompt += f"### System: {system_prompt}### User: {user_input}\n\n### Assistant:\n"

        inputs = tokenizer(prompt, return_tensors="pt").to("cuda")
        output = model.generate(**inputs, do_sample=True, top_p=0.95, top_k=0, max_new_tokens=4096)

        string = tokenizer.decode(output[0], skip_special_tokens=True)
        print(string)

        return string
    elif (model["name"] == "psmathur/orca_mini_v3_13b"):
        tokenizer = AutoTokenizer.from_pretrained(model["name"])
        model = AutoModelForCausalLM.from_pretrained(
            model["name"],
            torch_dtype=torch.float16,
            load_in_8bit=True,
            low_cpu_mem_usage=True,
            device_map="auto"
        )

        system_prompts = [entry['content'] for entry in conversation if entry['role'] == 'system']
        user_inputs = [entry['content'] for entry in conversation if entry['role'] == 'user']

        prompt = ""
        for system_prompt, user_input in zip(system_prompts, user_inputs):
            prompt += f"### System: {system_prompt}### User: {user_input}\n\n### Assistant:\n"

        inputs = tokenizer(prompt, return_tensors="pt").to("cuda")
        output = model.generate(**inputs, do_sample=True, top_p=0.95, top_k=0, max_new_tokens=4096)

        print(tokenizer.decode(output[0], skip_special_tokens=True))

        return string
    elif (model["name"] == "stabilityai/stablecode-completion-alpha-3b-4k"):
        from transformers import AutoModelForCausalLM, AutoTokenizer
        tokenizer = AutoTokenizer.from_pretrained(model["name"])
        model = AutoModelForCausalLM.from_pretrained(
            model["name"],
            trust_remote_code=True,
            torch_dtype="auto",
        )
        model.cuda()


        system_prompts = [entry['content'] for entry in conversation if entry['role'] == 'system']
        user_inputs = [entry['content'] for entry in conversation if entry['role'] == 'user']

        prompt = ""
        for system_prompt, user_input in zip(system_prompts, user_inputs):
            prompt += f"### System: {system_prompt}### User: {user_input}\n\n### Assistant:\n"


        inputs = tokenizer(prompt, return_tensors="pt").to("cuda")
        tokens = model.generate(
            **inputs,
            max_new_tokens=48,
            temperature=0.2,
            do_sample=True,
        )
        return tokenizer.decode(tokens[0], skip_special_tokens=True)
    else:
        openai_settings = config["openai_settings"]
        options = load_options()  # Load options including the API key
        url = "https://api.openai.com/v1/chat/completions"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f'Bearer {options["api_key"]}'
        }

        data = {
            "model": model["name"],  # Use model name from the passed model object
            "messages": conversation,
            "temperature": openai_settings["temperature"],
            "top_p": openai_settings["top_p"],
            "max_tokens": openai_settings["max_tokens"]
        }

        if openai_settings["streaming"]:
            data["stream"] = True

        response = requests.post(url, json=data, headers=headers)
        json_content = response.json()

        # print(json_content)
    
        return json_content["choices"][0]["message"]["content"]

# Other related functions
