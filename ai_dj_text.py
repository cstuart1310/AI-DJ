#generates text response
from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline

def setupTextModel(modelName,revisionName):
    print("Setting up text model...")
    try:#if the models can be found locally
        model = AutoModelForCausalLM.from_pretrained(modelName, local_files_only=True,revision=revisionName,device_map="auto",trust_remote_code=False,force_download=True)
        tokenizer = AutoTokenizer.from_pretrained(modelName, local_files_only=True,use_fast=True)
    except (AttributeError,OSError):#if the models cannot be found locally, downloads them and warns the user.
        print("Model'",modelName,"'with revision'",revisionName,"'is not found locally. Downloading now. This may take some time but only needs to be done once")
        model = AutoModelForCausalLM.from_pretrained(modelName,local_files_only=False,device_map="auto",trust_remote_code=False,revision=revisionName)
        tokenizer = AutoTokenizer.from_pretrained(modelName, use_fast=True)
        
    return model, tokenizer#returns the successfully downloaded/loaded model and tokenizer

def genResponse(songX,nameX,songY,nameY,model,tokenizer):#generates a text response using the chosen model
    prompt = 'Your role is a cool radio DJ. The song "songX" by "nameX" has just finished, what would you say in the intermission to transition to the song "songY" by "nameY"? Use puns if possible, and keep it to two sentences.'#main prompt
    
    #swaps song temps with actual values
    prompt = prompt.replace("songX",songX)
    prompt = prompt.replace("nameX",nameX)
    prompt = prompt.replace("songY",songY)
    prompt = prompt.replace("nameY",nameY)
    prompt_template=f'''Below is an instruction that describes a task. Write a response that appropriately completes the request.

    ## Instruction:
    {prompt}

    ## Response:
    '''
    print("Prompt:",prompt)
    print("Generating response...")
    input_ids = tokenizer(prompt_template, return_tensors='pt').input_ids.cuda()
    output = model.generate(inputs=input_ids, temperature=0.7, do_sample=True, top_p=0.95, top_k=40, max_new_tokens=512)
    response=(tokenizer.decode(output[0])).split("## Response:")[1]
    response=response.replace("</s>","")#removes tag generated by model
    print("Response:",response)
    return response


#change these to any LLM you want to test from huggingface
modelName = "TheBloke/storytime-13B-GPTQ"
revisionName = "main"

model,tokenizer=setupTextModel(modelName,revisionName)
with open("transitions.txt","r") as transitionsFile:
    transitionLines=transitionsFile.readlines()
for line in transitionLines:
    lineElements=line.split("|")
    songX=lineElements[0]
    songY=lineElements[1]
    nameX=lineElements[2]
    nameY=lineElements[3]
    audioFileName=lineElements[4].replace("\n","")#removes newline from end of line
    response=genResponse(songX,nameX,songY,nameY,model,tokenizer).replace("\n","")
    responseWrite=(songX+"|"+songY+"|"+response+"|"+audioFileName+"\n")
    print("Writing:",responseWrite)
    with open("responses.txt","a") as responseFile:
        responseFile.write(responseWrite)