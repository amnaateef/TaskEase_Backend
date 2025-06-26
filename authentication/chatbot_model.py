from transformers import AutoModelForCausalLM, AutoTokenizer
from torch.utils.data import Dataset, DataLoader # type: ignore

# Load pre-trained model and tokenizer for DialoGPT
tokenizer = AutoTokenizer.from_pretrained("microsoft/DialoGPT-medium")
model = AutoModelForCausalLM.from_pretrained("microsoft/DialoGPT-medium")

tokenizer.pad_token = tokenizer.eos_token  # Fix the missing pad_token error

training_data = [ 
    {"conversation": [
        {"role": "user", "content": "How do I hire an expert?"},
        {"role": "bot", "content": "You can hire an expert by browsing our expert list, selecting the expert that fits your needs, and then booking a task with them."}
    ]},
    {"conversation": [
        {"role": "user", "content": "I want to book an expert."},
        {"role": "bot", "content": "You can book an expert by selecting one based on your requirements and scheduling a task."}
    ]},
    {"conversation": [
        {"role": "user", "content": "What is the process for hiring an expert?"},
        {"role": "bot", "content": "You can browse through experts, select the one that fits your task, and then book them."}
    ]},
    {"conversation": [
        {"role": "user", "content": "Can I hire an expert for an urgent task?"},
        {"role": "bot", "content": "Yes, you can hire an expert for an urgent task. Check expert availability for urgent bookings."}
    ]},
    {"conversation": [
        {"role": "user", "content": "What tasks can I hire experts for?"},
        {"role": "bot", "content": "We have experts available for various tasks such as cleaning, plumbing, electrical work, and more."}
    ]},
    {"conversation": [
        {"role": "user", "content": "What services do the experts provide?"},
        {"role": "bot", "content": "Experts provide services like cleaning, plumbing, electrical work, and other household services."}
    ]},
    {"conversation": [
        {"role": "user", "content": "Can experts help with cleaning tasks?"},
        {"role": "bot", "content": "Yes, we have experts available for cleaning tasks such as house cleaning, office cleaning, and more."}
    ]},
    {"conversation": [
        {"role": "user", "content": "What type of plumbing services do experts provide?"},
        {"role": "bot", "content": "Experts offer services like leak repair, pipe installation, and clogged drain cleaning."}
    ]},
    {"conversation": [
        {"role": "user", "content": "What payment methods are available?"},
        {"role": "bot", "content": "We accept cash, credit cards, online, and bank transfers."}
    ]},
    {"conversation": [
        {"role": "user", "content": "How can I pay for the task?"},
        {"role": "bot", "content": "You can pay via cash, credit card, online, or bank transfer. Choose your preferred method while booking the task."}
    ]},
    {"conversation": [
        {"role": "user", "content": "Is payment secure?"},
        {"role": "bot", "content": "Yes, all transactions are securely processed using encryption protocols."}
    ]},
    {"conversation": [
        {"role": "user", "content": "Can I pay online?"},
        {"role": "bot", "content": "Yes, we accept payments online."}
    ]},
    {"conversation": [
        {"role": "user", "content": "Do I need to pay upfront?"},
        {"role": "bot", "content": "Yes, payment is generally required upfront to confirm the booking."}
    ]},
    {"conversation": [
        {"role": "user", "content": "When is expert Muhammad Raza available?"},
        {"role": "bot", "content": "Muhammad Raza is available Monday to Friday from 9 AM to 5 PM."}
    ]},
    {"conversation": [
        {"role": "user", "content": "What time is expert Sadia Irfan free?"},
        {"role": "bot", "content": "Sadia Irfan is available between 10 AM and 6 PM on weekdays."}
    ]},
    {"conversation": [
        {"role": "user", "content": "Is expert Hashim available tomorrow?"},
        {"role": "bot", "content": "Hashim is available tomorrow, but you may need to confirm the exact time."}
    ]},
    {"conversation": [
        {"role": "user", "content": "How can I book an expert for the weekend?"},
        {"role": "bot", "content": "You can book an expert for the weekend by selecting their available times on the booking page."}
    ]},
    {"conversation": [
        {"role": "user", "content": "Has my booking been confirmed?"},
        {"role": "bot", "content": "You can check the task details on your profile page."}
    ]},
    {"conversation": [
        {"role": "user", "content": "When will my task be completed?"},
        {"role": "bot", "content": "Your task will be completed by the expert on the scheduled date."}
    ]},
    {"conversation": [
        {"role": "user", "content": "Can I change my booking?"},
        {"role": "bot", "content": "You can change your booking by contacting support or updating it through your profile page."}
    ]},
    {"conversation": [
        {"role": "user", "content": "How can I cancel my booking?"},
        {"role": "bot", "content": "You can cancel your booking by visiting your task page or contacting customer support."}
    ]},
    {"conversation": [
        {"role": "user", "content": "Hello"},
        {"role": "bot", "content": "Hello! How can I assist you today?"}
    ]},
    {"conversation": [
        {"role": "user", "content": "Hi, how are you?"},
        {"role": "bot", "content": "I'm doing well! How can I help you?"}
    ]},
    {"conversation": [
        {"role": "user", "content": "Good morning"},
        {"role": "bot", "content": "Good morning! How may I assist you today?"}
    ]},
    {"conversation": [
        {"role": "user", "content": "Hey, I need help"},
        {"role": "bot", "content": "Hi there! How can I assist you today?"}
    ]},
    {"conversation": [
        {"role": "user", "content": "Goodbye"},
        {"role": "bot", "content": "Goodbye! Have a great day!"}
    ]},
    {"conversation": [
        {"role": "user", "content": "Thanks for your help"},
        {"role": "bot", "content": "You're welcome! Have a nice day!"}
    ]},
    {"conversation": [
        {"role": "user", "content": "Thank you"},
        {"role": "bot", "content": "You're welcome! Let me know if you need anything else."}
    ]},
    {"conversation": [
        {"role": "user", "content": "Many thanks"},
        {"role": "bot", "content": "You're welcome! Feel free to ask if you need anything else."}
    ]},
    {"conversation": [
        {"role": "user", "content": "Sorry"},
        {"role": "bot", "content": "No worries! Let me know how I can assist you further."}
    ]},
    {"conversation": [
        {"role": "user", "content": "How do I leave a review?"},
        {"role": "bot", "content": "You can leave a review after your task is completed through your profile page."}
    ]},
    {"conversation": [
        {"role": "user", "content": "What’s your cancellation policy?"},
        {"role": "bot", "content": "You can cancel the task within 24 hours of booking. Check our terms for more details."}
    ]},
    {"conversation": [
        {"role": "user", "content": "How do I contact support?"},
        {"role": "bot", "content": "You can contact support via email or through the contact page."}
    ]},
    {"conversation": [
        {"role": "user", "content": "Do you have any discount offers?"},
        {"role": "bot", "content": "We offer seasonal promotions. You can check for current discounts on our website."}
    ]},
    {"conversation": [
        {"role": "user", "content": "Are services available 24/7?"},
        {"role": "bot", "content": "Our experts are available Monday to Friday, 9 AM to 6 PM. Some experts may have weekend availability."}
    ]},
    {"conversation": [
        {"role": "user", "content": "How do I get a refund?"},
        {"role": "bot", "content": "If you're dissatisfied with the task, you can apply for a refund by contacting support."}
    ]},
    {"conversation": [
        {"role": "user", "content": "What are the terms and conditions?"},
        {"role": "bot", "content": "Please read our terms and conditions on the website for full details."}
    ]},
    {"conversation": [
        {"role": "user", "content": "Can I change the expert after booking?"},
        {"role": "bot", "content": "Yes, you can change the expert by contacting support before the task starts."}
    ]}
]


# Convert conversation pairs into a format suitable for training
class ChatbotDataset(Dataset):
    def __init__(self, data):
        self.data = data
        self.encodings = []
        self.labels = []

        for conv in data:
            user_input = conv["conversation"][0]["content"]
            bot_response = conv["conversation"][1]["content"]

            # Encoding user input and bot response
            encoding = tokenizer(user_input + tokenizer.eos_token + bot_response + tokenizer.eos_token,
                                 return_tensors="pt", truncation=True, padding="max_length", max_length=512)
            self.encodings.append(encoding["input_ids"].squeeze())
            self.labels.append(encoding["input_ids"].squeeze())

    def __len__(self):
        return len(self.data)

    def __getitem__(self, idx):
        return {"input_ids": self.encodings[idx], "labels": self.labels[idx]}

# Instantiate the dataset and dataloader
train_dataset = ChatbotDataset(training_data)
print(f"Training data length: {len(train_dataset)}")
train_dataloader = DataLoader(train_dataset, batch_size=2, shuffle=True)

# Fine-tuning the model
from transformers import Trainer, TrainingArguments

training_args = TrainingArguments(
    output_dir="./chatbot_model",  # where to save the model
    num_train_epochs=3,           # number of training epochs
    per_device_train_batch_size=2,  # batch size
    save_steps=1000,
    save_total_limit=2,
)

trainer = Trainer(
    model=model,                          # pre-trained model
    args=training_args,                   # training arguments
    train_dataset=train_dataset,          # training dataset
)

trainer.train()

# Save the fine-tuned model
model.save_pretrained("./chatbot_model")
tokenizer.save_pretrained("./chatbot_model")

# Function to get a response from the chatbot
def chatbot_response(user_input):
    new_user_input_ids = tokenizer.encode(user_input + tokenizer.eos_token, return_tensors='pt')
    chat_history_ids = model.generate(new_user_input_ids, max_length=1000, pad_token_id=tokenizer.eos_token_id)
    bot_reply = tokenizer.decode(chat_history_ids[:, new_user_input_ids.shape[-1]:][0], skip_special_tokens=True)
    return bot_reply
