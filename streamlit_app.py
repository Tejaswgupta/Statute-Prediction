
from openai import AzureOpenAI
import streamlit as st 
import re

client = AzureOpenAI(
    api_key="e5a86e5ac7ce453a8fae2dcbfaafbef7", 
    api_version="2023-07-01-preview",
    azure_endpoint="https://votum.openai.azure.com/",
)


fact = '''In service Mr. In-charge Inspector Mr. City of Police Station Kotwali Mr. G Candidate Chetna Gupta alias Chanchal Gupta Advocate Resident of Flat No., 76/44 Halsey Road Kanpur Nagar and practicing law from a pucca chamber just in front of CMO office at Kachehri. On 2024, at around 8: 30 am, my chamber suddenly caught fire and at around 9: 00 am, I got a call informing me that my chamber was on fire. I reached the chamber immediately. By then, Manish, who was cleaning my chamber, was dousing the fire with water. All my chamber's luggage, files, AC, sofa wings, amalt glass walls, necessary documents, miscellaneous items, etc. have been destroyed. I am informing the concerned post. Please take appropriate action. Dated 29. 2024 Signature English unreadable Candidate Chetna Gupta alias Chanchal Gupta Md. 7376222267 Note I hereby certify that 674 Dhirendra Pratap Singh, permanent & tahrir copy of the complaint was literally typed by me on the computer 5057 Lalit Kumar. That I attest to.'''

prompt = """Task: Given examples of a Supreme Court case and the statutes applied in that case, your objective is to make accurate predictions of the specific charge or statute that is most likely to be applied within the context of the case delimited by triple backticks (```), ensuring exact predictions and learning from the provided examples.You should only include the statutes it is most confident about.The response format should include the statutes applied as in the context.
                            You should to showcase creativity and knowledge to enhance the accuracy of statute predictions based on the given fact statement.

Context:

Fact Statement:"In this one gets used to writing common orders, for orders are written either on behalf of the [PRODUCT], or on behalf of the [ORG].
While endorsing the opinion expressed by [PERSON],, adjudicating upon the prayer for my recusal, from hearing the matters in hand, reasons for my continuation on the [ORG], also need to be expressed by me.
It has been necessitated, for deciding an objection, about the present composition of the [PERSON].
As already noted above,, [ORG] has rendered the decision on the objection.
The events which followed the order of [PERSON],, are also of some significance.
In my considered view, they too need to be narrated, for only then, the entire matter can be considered to have been fully expressed, as it ought to be.
I also need to record reasons, why my continuation on the reconstituted [ORG], was the only course open to me.
And therefore, my side of its understanding, dealing with the perception, of the other side of the [PRODUCT].
Union of India [DATE] Indlaw SCO 185 Writ Petition C no.13 of, Mr. [PERSON], Senior Advocate, in [ORG] of [DATE], Mr. [PERSON], Advocate, in [ORG] Indlaw SC 29 Writ Petition C [DATE] and Mr. [PERSON], Advocate, in Change [GPE] v. [ORG] no.70 of [DATE], representing the petitioners were heard.iii The proceedings recorded by this [ORG] on 18.3.2015 reveal, that Mr. [PERSON], in Writ Petition C no.70 of [DATE] was heard again on, whereupon, Mr. [PERSON] and Mr., [ORG] [GPE], also made their submissions.
[CARDINAL]. Based on the order passed by the Judge [PERSON] on 7.4.2015, Honble the Chief Justice of [GPE], constituted a [CARDINAL] Judge [PERSON], comprising of,,, and, JJ.
[CARDINAL]. On 13.4.2015 the Constitution Ninety ninth Amendment Act, [DATE], and [ORG] Act, [DATE], were notified in the Gazette of India Extraordinary.Both the above enactments, were brought into force with effect from 13.4.2015.
[CARDINAL]. When the reconstituted [PERSON] commenced hearing on 21.4.2015, Mr. made a prayer for my recusal from the [PRODUCT], which was seconded by Mr. Mathews [PERSON] petitioner in- person in Writ Petition C no.124 of [DATE], the latter advanced submissions, even though he had been barred from doing so, by an earlier order dated 24.3.2015 extracted above.
The [ORDINAL] judgment was rendered, by a [CARDINAL] Judge [PERSON], by a majority of [CARDINAL], in the [ORDINAL] Judges case on [CARDINAL]. The correctness of the First Judges case was doubted by a Judge [PERSON] in of [GPE], [DATE] Supp 1 SCC 574 [ORG] [CARDINAL], which opined that the majority view, in the [ORG] case, should be considered by a larger.
The amendment, received the assent of the President on [DATE].It was however given effect to, with effect from 13.4.2015 consequent upon its notification in the Gazette of India Extraordinary Part II, [SECTION_UNK].
The same was also brought into force, with effect from 13.4.2015 by its notification in the Gazette of India Extraordinary Part II, [SECTION_UNK].
The Judges case- [DATE] [EVENT] 87 [DATE] [ORG] [CARDINAL].[DATE].The Union Law Minister addressed a letter dated 18.3.1981 to the Governor of [PRODUCT] and to Chief Ministers of all other [GPE].
The addressees were inter [PERSON], [CARDINAL] of [ORG], should as far as possible be from outside the in which is situated.
Through the above letter, the addressees were requested to.a obtain from all additional Judges working in the High Courts.their consent to be appointed as permanent Judges in any other in the country.
The above noted letter required, that the concerned appointees.be required to name [CARDINAL] High Courts, in order of preference, to which they would prefer to be appointed as permanent Judges and b obtain from persons who have already been or may in the future be proposed by you for initial appointment their consent to be appointed to any other [ORG] in the country along with a similar preference for [CARDINAL] High Courts.
The Union Law Minister, in the above letter clarified, that furnishing of their consent or indication of their preference, would not imply any commitment, at the behest of the Government, to accommodate them in accordance with their preferences.
In response, quite a few additional Judges, gave their consent to be appointed outside their parent [ORG].
A series of [ORG] in [GPE] passed resolutions, condemning the letter dated 18.3.1981, as being subversive of judicial independence.
Since that was not done, a writ petition was filed by the above Associations in the Bombay High Court, challenging the letter dated 18.3.1981.
An interim order was passed by [ORG], restraining the Union Law Minister and the Government from implementing the letter dated 18.3.1981.
While the matter was pending before this, the Union Law Minister and, filed a transfer petition under [LAW] The transfer petition was allowed, and the writ petition filed in the Bombay High Court, was transferred to [ORG].
These short term appointments were assailed, as being unjustified under [LAW], besides being subversive of the independence of the judiciary."

Statutes:['Constitution_226', 'Constitution_136', 'Constitution_14', 'Constitution_16', 'Constitution_227', 'Constitution_133', 'Constitution_246', 'Constitution_1', 'Constitution_21', 'Constitution_32', 'Constitution_19', 'Constitution_141', 'Constitution_4', 'Constitution_31', 'Constitution_12', 'Constitution_2', 'Constitution_39', 'Constitution_311', 'Constitution_13', 'Constitution_5', 'Constitution_3', 'Constitution_6', 'Constitution_15']

###

Format your response as follows:
"Statutes applied: [List of applicable statutes]"

Instructions:

Learn from the examples provided in the context to understand the task of charge or statute prediction.
Your response should be focused on providing the exact statute or charge that aligns with the legal principles and precedents applicable to the given facts.
In your response, include only the statutes you are most confident about.Ensure that the statutes generated as responses are valid and recognized legal statutes. Avoid generating fabricated or invalid statutes.
The model's performance will be evaluated based on its ability to predict the correct statute, include only confident statutes, and showcase creativity in its predictions.

Fact Statement: ```{fact}```
"""

def generate(input_text):
    print(input_text)
    
    com = prompt.format(fact=input_text)
    chat_completion = client.chat.completions.create(
        model="gpt-4-turbo",
        temperature=0.5,
        messages=[
                {"role": "system", "content": "You are a legal assistant from India, skilled in and tagging applicable legal statutes to FIR(First Information Report)."},
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

  
# Streamlit app layout  
st.title('FIR Statutes Prediction')  
  

# Button to pre-fill the FIR input with hardcoded text  
if st.button('Load Example FIR'):  
    input_fir = fact  
else:  
    input_fir = ""  
  
# Text input for FIR  
fir_text = st.text_area("Enter the FIR:", value=input_fir, height=300)  

  
# Button to predict statutes  
if st.button('Predict Statutes'):  
    if fir_text:  
        with st.spinner('Predicting...'):  
            print(fir_text)
            gpt_output = generate(fir_text)  
            print(gpt_output)
            statutes_list = extract_statutes(gpt_output)  
            if statutes_list:  
                st.subheader('Predicted Statutes')  
                for statute in statutes_list:  
                    st.write(f"- {statute}")  
            else:  
                st.warning('No statutes were predicted. Please check the FIR text and try again.')  
    else:  
        st.warning('Please enter the FIR text to predict statutes.')  

