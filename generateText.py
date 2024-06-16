#generates text response
from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline

def genResponse(songX,nameX,songY,nameY):
    model_name_or_path = "TheBloke/storytime-13B-GPTQ"
    model = AutoModelForCausalLM.from_pretrained(model_name_or_path,
                                                device_map="auto",
                                                trust_remote_code=False,
                                                revision="main")

    tokenizer = AutoTokenizer.from_pretrained(model_name_or_path, use_fast=True)

    prompt = 'Your role is a cool radio DJ. The song "songX" by "nameX" has just finished, what would you say in the intermission to transition to the song "songY" by "nameY"? Use puns if possible, and keep it to two sentences.'
    prompt_template=f'''Below is an instruction that describes a task. Write a response that appropriately completes the request.

    ## Instruction:
    {prompt}

    ## Response:
    '''

    prompt = prompt.replace("songX",songX)
    prompt = prompt.replace("nameX",nameX)
    prompt = prompt.replace("songY",songY)
    prompt = prompt.replace("nameY",nameY)

    print("Prompt:",prompt)
    print("Generating response...")
    input_ids = tokenizer(prompt_template, return_tensors='pt').input_ids.cuda()
    output = model.generate(inputs=input_ids, temperature=0.7, do_sample=True, top_p=0.95, top_k=40, max_new_tokens=512)
    response=(tokenizer.decode(output[0]))
    print("Response:",response)
    return response