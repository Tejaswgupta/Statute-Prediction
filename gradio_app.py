import requests, uuid, json
from openai import AzureOpenAI,OpenAI
import re
import gradio as gr
import csv
import random

client = AzureOpenAI(
    api_key="226e96dc78fb49b3bcd143aa8b191dd2", 
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
Fact Statement:"Copying Tahrir Hindi plaintiff ................... In service Mr. SHO Akrabad Aligarh The request is that I am Rahul Kumar S/0 Gopal resident of Vijaygarh Chauraha Police Station Akrabad Aligarh, today on 30/4/2021 at around 7 o'clock in the evening I was sitting at my coke shop, Deepu, Kalu, Karthik, Dinesh, Saunu, came to me and started saying that you ask for a lot of money, now tell you that then the above people called their colleagues and called  And all of them unanimously started beating me and my sister Neelam, due to which my sister's clothes were torn, hearing the noise, Ramu Sunil, many people came from nearby, then all these people started running threatening to kill and then Kalu S/0 Dinanath resident of Kuagaon, Karthik S/0 Devendra,  Deepu fired at me with the intention of killing me, in which a fire has hit the thumb of my left hand, due to which I have suffered a lot of injury and bleeding, so I request sir to please file my report Signature Rahul Applicant Rahul S/0 Gopal R/o Vijaygarh Chauraha Police Station Akhrabad Aligarh Mo0 8126303026 Date30/4/2021 Author: Narasimma Pawar S/0 Rambabu Powerhouse, Karhala Road, Mau0 908400582 Note: I am CC 551 Sanjeev Kumar certifying that the copy of Tahrir has been recorded on the computer word and word"

Statutes:['IPC_323', 'IPC_354', 'IPC_307', 'IPC_506']
-----

###

Format your response as follows:
"Statutes applied: [List of applicable statutes]"

Instructions:

Learn from the examples provided in the context to understand the task of charge or statute prediction.
Your response should be focused on providing the exact statute or charge that aligns with the legal principles and precedents applicable to the given facts.
In your response, include only the statutes you are most confident about.Ensure that the statutes generated as responses are valid and recognized legal statutes applicable in FIRs. In certain cases you can also apply sections from special acts including but not limited to 'The_Arms_Act_27' , 'The_Motor_Vehicles_Act_1988', 'Dowry_Prohibition_Act_1961', like 'Dowry_Prohibition_Act_1961_3'. Avoid generating fabricated or invalid statutes.
Think step by step to cover all possible statutes that are relevant to the fact statement.

Fact Statement: ```{fact}```
"""

prompt_new = '''Prompt:
Task: Analyze the provided First Information Report (FIR) and predict the most relevant legal statutes and sections that apply to the described incident. Your response should be based on the specific details contained within the FIR. When predicting, you should consider the Indian Penal Code (IPC) and other special acts such as the Protection of Children from Sexual Offences (POCSO) Act, the Motor Vehicles Act, etc. Ensure that your predictions are precise and reflect an understanding of the legal context of the FIR. Your response should be formulated as a list of statutes and sections, including the appropriate act name followed by the section number, e.g., 'IPC_323', 'POCSO_7', 'Motor_Vehicles_Act_1988_184'. Avoid predicting statutes that are not directly supported by the facts of the case. Be thorough and deliberate in your reasoning.

Context:
-----
Fact Statement:"In service Mr. SHO Akrabad Aligarh The request is that I am Rahul Kumar S/0 Gopal resident of Vijaygarh Chauraha Police Station Akrabad Aligarh, today on 30/4/2021 at around 7 o'clock in the evening I was sitting at my coke shop, Deepu, Kalu, Karthik, Dinesh, Saunu, came to me and started saying that you ask for a lot of money, now tell you that then the above people called their colleagues and called  And all of them unanimously started beating me and my sister Neelam, due to which my sister's clothes were torn, hearing the noise, Ramu Sunil, many people came from nearby, then all these people started running threatening to kill and then Kalu S/0 Dinanath resident of Kuagaon, Karthik S/0 Devendra,  Deepu fired at me with the intention of killing me, in which a fire has hit the thumb of my left hand, due to which I have suffered a lot of injury and bleeding, so I request sir to please file my report Signature Rahul Applicant Rahul S/0 Gopal R/o Vijaygarh Chauraha Police Station Akhrabad Aligarh Mo0 8126303026 Date30/4/2021 Author: Narasimma Pawar S/0 Rambabu Powerhouse, Karhala Road, Mau0 908400582 Note: I am CC 551 Sanjeev Kumar certifying that the copy of Tahrir has been recorded on the computer word and word"

Statutes:['IPC_323', 'IPC_354', 'IPC_307', 'IPC_506']
-----
 
 
Instructions:
- Carefully read the FIR to understand the nature of the incident and the actions of the involved parties.
- Identify specific actions described in the FIR that may correspond to legal offenses under the IPC or other relevant special acts.
- Predict the statutes by considering both the actions and the intent of the parties involved, as inferred from the FIR.
- Only include those statutes and sections for which there is clear evidence in the FIR. If the information provided does not support the application of a particular statute or section, do not include it.
- Ensure that the statutes and sections are currently in force and applicable within the jurisdiction of the FIR.
- Prioritize accuracy and relevancy in your predictions over the quantity of statutes listed

Provide a list of applicable statutes and sections in a clear and organized format like follows.
"Statutes applied: [List of applicable statutes]"
Fact Statement: "{fact}"
'''

prompt_new_2 = '''You are an AI trained to predict the most applicable legal statutes and sections based on the content of a First Information Report (FIR). Below are examples of FIRs with the correctly applied statutes. Learn from these examples to accurately predict the statutes for a new FIR.
In your response, include only the statutes you are most confident about.Ensure that the statutes generated as responses are valid and recognized legal statutes applicable in FIRs. In certain cases you can also apply sections from special acts including but not limited to 'The_Arms_Act_27' , 'The_Motor_Vehicles_Act_1988', 'Dowry_Prohibition_Act_1961', like 'Dowry_Prohibition_Act_1961_3'. Avoid generating fabricated or invalid statutes.

Example 1:
Fact Statement: "The complainant reported that their vehicle was stolen from outside their residence on the night of 5th April. The keys had been left in the ignition."
Statutes Applied: ['IPC_379', 'Motor_Vehicles_Act_1988_39']

Example 2:
Fact Statement: "An underage victim reported being touched inappropriately by an adult neighbor. The incident occurred when the victim was alone at home."
Statutes Applied: ['IPC_354', 'POCSO_7', 'POCSO_8']

Example 3:
Fact Statement: "During a routine traffic stop, the driver was found to be under the influence of alcohol. They were driving without a license and caused an accident resulting in minor injuries to a pedestrian."
Statutes Applied: ['IPC_279', 'IPC_337', 'Motor_Vehicles_Act_1988_185', 'Motor_Vehicles_Act_1988_3']

Now, predict the statutes for the following Fact Statement:

Fact Statement: ```{fact}```
'''


def generate(input_text):
    com = prompt_new_2.format(fact=input_text)
    print(input_text)
    chat_completion = mistral_client.chat.completions.create(
        # model="gpt-4-turbo",
        model='Qwen/Qwen1.5-14B-Chat-GPTQ-Int4',
        temperature=0.5,
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


  
  

# def get_random_sample():
#     filename = "Apr.csv"  # Replace 'your_file.csv' with your actual file path
#     with open(filename, 'r', newline='') as csvfile:
#         # Step 3: Read all rows into a list
#         reader = csv.reader(csvfile)
#         rows = [row for row in reader]

#         # Step 4: Generate a random index
#         random_index = random.randint(0, len(rows) - 1)
#         print(ra)

#         # Step 5: Retrieve the row at the random index
#         random_row = rows[random_index]

#         # Step 6: Print or process the random row
#         return random_row

# example = get_random_sample()


def predict_statutes(fir_text,language):  
    if language == 'Hindi':
        text = translate(fir_text)
    else:
        text = fir_text
    
    if text:  
        gpt_output = generate(text)  
        statutes_list = extract_statutes(gpt_output)  
        if statutes_list:  
            return "\n".join(f"- {statute}" for statute in statutes_list)
        else:  
            return "No statutes were predicted. Please check the FIR text and try again."
    else:  
        return "Please enter the FIR text to predict statutes."

demo = gr.Interface(
    title='Statute Prediction',
    description='Uses AI to analyze the FIR content and intelligently predict applicable statutes',
    fn=predict_statutes,  
    inputs=[gr.Textbox(label="Enter the FIR:", placeholder="Type or paste the FIR here...", lines=10),   
            gr.Dropdown(label="Select Language", choices=["English", "Hindi"], value="English"),
            # gr.Slider(minimum=0.1,maximum=1.0,value=0.5,step=0.1),
            ],
    outputs=[gr.Textbox(label="Predicted Statutes")],  
    # examples=[[example[5], "English"]],  
)  
  
demo.launch()



#  GRADIO_SERVER_NAME=0.0.0.0 GRADIO_SERVER_PORT=7862 gradio gradio_app.py 

