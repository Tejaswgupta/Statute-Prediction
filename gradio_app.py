import requests, uuid, json
from openai import AzureOpenAI,OpenAI
import re
import gradio as gr
import csv
import random

client = AzureOpenAI(
    api_key="e5a86e5ac7ce453a8fae2dcbfaafbef7", 
    api_version="2023-07-01-preview",
    azure_endpoint="https://votum.openai.azure.com/",
)

mistral_client = OpenAI(
    api_key='EMPTY',
    base_url="http://20.124.240.6:8083/v1",
)


fact_example = '''In service Mr. In-charge Inspector Mr. City of Police Station Kotwali Mr. G Candidate Chetna Gupta alias Chanchal Gupta Advocate Resident of Flat No., 76/44 Halsey Road Kanpur Nagar and practicing law from a pucca chamber just in front of CMO office at Kachehri. On 2024, at around 8: 30 am, my chamber suddenly caught fire and at around 9: 00 am, I got a call informing me that my chamber was on fire. I reached the chamber immediately. By then, Manish, who was cleaning my chamber, was dousing the fire with water. All my chamber's luggage, files, AC, sofa wings, amalt glass walls, necessary documents, miscellaneous items, etc. have been destroyed. I am informing the concerned post. Please take appropriate action. Dated 29. 2024 Signature English unreadable Candidate Chetna Gupta alias Chanchal Gupta Md. 7376222267 Note I hereby certify that 674 Dhirendra Pratap Singh, permanent & tahrir copy of the complaint was literally typed by me on the computer 5057 Lalit Kumar. That I attest to.''' 

prompt = """Task: Given examples of an FIR and the statutes applied in that case, your objective is to make accurate predictions of the specific charge or statute that is most likely to be applied within the context of the case delimited by triple backticks (```), ensuring exact predictions and learning from the provided examples.You should only include the statutes it is most confident about.The response format should include the statutes applied as in the context.
You should to showcase creativity and knowledge to enhance the accuracy of statute predictions based on the given fact statement.

Context:
-----
Fact Statement:"Nakal Tahrir Hindi Plaintiff Service in Mr. SHO Sir Police Station Akrawad District Aligarh Sir, today on 24/4/2021, I along with Deputy Inspector Kapil Dev Maya Hamrah Ka0 406 Narsingh was in the police station area in the police station area to effectively follow the preventive action and public to follow the public in connection with the election. Ravindra Giri, a candidate for the post of panchayat member, along with his supporters, has violated the rules of code of conduct and public care by violating Section 144 CrPC by violating Section 144 CrPC by violating the campaign vehicle UP 86 T 5771 MAX without any permission in his favor with his supporters. In which there was full possibility of spreading the infection, the documents of the said vehicle were asked from the candidate Ravindra Giri, then the vehicle number UP 86 T 5771 was seized under section 207 MV Act and Gavendra Giri son of Moti Giri and Jitendra Giri son of Ramprakash Giri and Gaurav Giri son of Jugendra Giri Ni0 Gana Kathera police station Vijaygarh district Aligarh and Yogesh Kumar son of Rajendra Singh Ni0wari police station Vijaygarh district Aligarh The offence of IPC reaches the extent of Section 188/269/171 C IPC and Epidemic Act. Sir, I request you to please register a case against the said accused and take necessary action. S.C. English U.P. Kapil Dev 24/4/21 Kapil Dev SI PS Akrawad Aligarh In the note CC 686 Yashpal Singh certifies that the copy of Tahrir has been marked as word and word."

Statutes:['IPC_188', 'IPC_269', 'IPC_171C', 'The_Motor_Vehicles_Act_1988_207']
-----

###

Format your response as follows:
"Statutes applied: [List of applicable statutes]"

Instructions:

Learn from the examples provided in the context to understand the task of charge or statute prediction.
Your response should be focused on providing the exact statute or charge that aligns with the legal principles and precedents applicable to the given facts.
In your response, include only the statutes you are most confident about.Ensure that the statutes generated as responses are valid and recognized legal statutes applicable in FIRs. In certain cases you can also apply sections from special acts including but not limited to 'The_Arms_Act_27' , 'The_Motor_Vehicles_Act_1988', 'Dowry_Prohibition_Act_1961', like 'Dowry_Prohibition_Act_1961_3'. Avoid generating fabricated or invalid statutes.
The model's performance will be evaluated based on its ability to predict the correct statute, include only confident statutes.
Think step by step to cover all possible statutes that are relevant to the fact statement.

Fact Statement: ```{fact}```
"""

def generate(input_text):
    com = prompt.format(fact=input_text)
    print(input_text)
    chat_completion = mistral_client.chat.completions.create(
        # model="gpt-4-turbo",
        model='Qwen/Qwen1.5-72B-Chat-GPTQ-Int4',
        temperature=0.3,
        messages=[
                {"role": "system", "content": "You are a helpful assistant who is expert in tagging FIRs with relevant statutes from IPC among other special acts."},
            {
                "role": "user",
                "content": com,
            }
        ],
    )
    print(chat_completion)
    return chat_completion.choices[0].message.content

def extract_statutes(gpt_output):  
    # Regular expression to match statutes within brackets  
    statutes = re.findall(r'\[([^\]]+)\]', gpt_output)  
    if statutes:  
        # Split the string into a list on comma followed by space  
        return statutes
    return []  

def translate(text):
    # Add your key and endpoint
    key = "8760fcb757fe44a19d3ec590cb80836f"
    endpoint = "https://api.cognitive.microsofttranslator.com"

    # location, also known as region.
    # required if you're using a multi-service or regional (not global) resource. It can be found in the Azure portal on the Keys and Endpoint page.
    location = "centralindia"

    path = '/translate'
    constructed_url = endpoint + path

    params = {
        'api-version': '3.0',
        'from': 'hi',
        'to': 'en',
    }

    headers = {
        'Ocp-Apim-Subscription-Key': key,
        'Ocp-Apim-Subscription-Region': location,
        'Content-type': 'application/json',
        'X-ClientTraceId': str(uuid.uuid4())
    }

    # You can pass more than one object in body.
    body = [{
        'text': text
    }]

    request = requests.post(constructed_url, params=params, headers=headers, json=body)
    return request.json()[0]['translations'][0]['text']


  
  

def get_random_sample():
    filename = "Apr.csv"  # Replace 'your_file.csv' with your actual file path
    with open(filename, 'r', newline='') as csvfile:
        # Step 3: Read all rows into a list
        reader = csv.reader(csvfile)
        rows = [row for row in reader]

        # Step 4: Generate a random index
        random_index = random.randint(0, len(rows) - 1)
        print(ra)

        # Step 5: Retrieve the row at the random index
        random_row = rows[random_index]

        # Step 6: Print or process the random row
        return random_row

example = get_random_sample()


def predict_statutes(fir_text,language):  
    if language == 'Hindi':
        text = translate(fir_text)
    else:
        text = fir_text
    
    ac_statute= example[-1] if fir_text==example[5] else ''
    
    if text:  
        gpt_output = generate(text)  
        statutes_list = extract_statutes(gpt_output)  
        if statutes_list:  
            return ("\n".join(f"- {statute}" for statute in statutes_list),ac_statute)
        else:  
            return ("No statutes were predicted. Please check the FIR text and try again.",ac_statute)
    else:  
        return ("Please enter the FIR text to predict statutes.",ac_statute)

demo = gr.Interface(
    title='Statute Prediction',
    description='Uses AI to analyze the FIR content and intelligently predict applicable statutes',
    fn=predict_statutes,  
    inputs=[gr.Textbox(label="Enter the FIR:", placeholder="Type or paste the FIR here...", lines=10),   
            gr.Dropdown(label="Select Language", choices=["English", "Hindi"], value="English"),
            # gr.Slider(minimum=0.1,maximum=1.0,value=0.5,step=0.1),
            ],
    outputs=[gr.Textbox(label="Predicted Statutes"),gr.Textbox(label="Actual Statutes",value=example[-1])],  
    examples=[[example[5], "English"]],  
)  
  
demo.launch()



#  GRADIO_SERVER_NAME=0.0.0.0 GRADIO_SERVER_PORT=7862 gradio gradio_app.py 

