guide for chatbot:

1. enter env 

2. pip install transformers and torch

2. run this command: 
python chatbot_model.py
this will train the model with pre-coded entries 
(38 and relevant to our project) since otherwise the 
file size is too large for GitHub.

3. run the Django server

4. download postman or any other client to sent POST 
requests in a JSON format (body raw) to get answers at http://127.0.0.1:8000/api/chatbot/get-bot-reply/
