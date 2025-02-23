
#This is the file that is used to finetune the Hugging Face T5-Small Model
#This will also be the file that will return a string response, the financial
#incedent report

from langchain_huggingface import HuggingFacePipeline
from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline

model_name = "distilgpt2" 
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForCausalLM.from_pretrained(model_name)
clea
hf_pipeline = pipeline(
    "text-generation", 
    model=model, 
    tokenizer=tokenizer, 
    max_length=300,       
    num_return_sequences=1, 
    no_repeat_ngram_size=2,  
    pad_token_id=tokenizer.eos_token_id, 
)


llm = HuggingFacePipeline(pipeline=hf_pipeline)


def generate_response(input_text):

    prompt = f"Human: {input_text}\nAI:"
    response = llm(prompt)
    

    print(f"Debug response: {response}")
    
    if isinstance(response, list) and isinstance(response[0], str):
        return response[0].strip().replace("Human:", "").replace("AI:", "")
    elif isinstance(response, str):
        return response.strip().replace("Human:", "").replace("AI:", "")
    else:
        return "Sorry, I couldn't generate a response."

while True:
    user_input = input("You: ")
    if user_input.lower() in ['exit', 'quit', 'bye']:
        print("AI: It was great talking with you! Take care!")
        break
    response = generate_response(user_input)
    print(f"AI: {response}")
