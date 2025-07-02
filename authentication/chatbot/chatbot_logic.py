from transformers import AutoModelForCausalLM, AutoTokenizer
import torch

model = None
tokenizer = None

def get_model():
    global model, tokenizer
    if model is None or tokenizer is None:
        # Use a valid HuggingFace model name
        model = AutoModelForCausalLM.from_pretrained("microsoft/DialoGPT-medium")
        tokenizer = AutoTokenizer.from_pretrained("microsoft/DialoGPT-medium")
    return model, tokenizer

# Function to get a response from the chatbot
def chatbot_response(user_input, chat_history_ids=None):
    model, tokenizer = get_model()
    new_user_input_ids = tokenizer.encode(user_input + tokenizer.eos_token, return_tensors='pt')

    # If there's a chat history, append it to the new input
    if chat_history_ids is not None:
        bot_input_ids = torch.cat([chat_history_ids, new_user_input_ids], dim=-1)
    else:
        bot_input_ids = new_user_input_ids

    chat_history_ids = model.generate(bot_input_ids, max_length=1000, pad_token_id=tokenizer.eos_token_id)

    # Decode the output (skip special tokens)
    bot_reply = tokenizer.decode(chat_history_ids[:, bot_input_ids.shape[-1]:][0], skip_special_tokens=True)
    
    return bot_reply, chat_history_ids
