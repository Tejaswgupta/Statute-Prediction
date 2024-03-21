import asyncio
import json
import re
from collections import deque

import asyncpg
import psycopg2
from langchain.chains.summarize import load_summarize_chain
from langchain.chat_models import AzureChatOpenAI, ChatOpenAI
from langchain.schema import Document, HumanMessage, SystemMessage
from langchain.text_splitter import RecursiveCharacterTextSplitter

json_obj = """{
  "statutes": [
    {
      "name": "",
      "specific_sections": [],
      "context": ""
    }
  ],
  "precedents": [
    {
      "case_name": "",
      "citation": "",
      "quoted_text": "",
      "principle_addressed": "",
      "outcome": "",
      "context": ""
    }
  ]
}"""

extraction_prompt = '''
---
Case Chunk (Part {i} of {l}):    
{c}
---  

---
Metadata:
{metadata}
---

Please read the above excerpt from a legal case carefully, and also analyze the metadata extracted by an LLM from previous chunks. Identify and extract any mentioned statutes (laws) and precedents (previous court decisions), and include the following details:  

For statutes, please provide:  
- The name of the statute  
- The specific sections or clauses cited  
- Any relevant quoted text from the statute  
- The context in which the statute is discussed  

For precedents, please provide:  
- The case name of the precedent  
- The citation (volume, reporter, and page number)  
- Any relevant quoted text from the precedent  
- The principle or legal issue that the precedent addresses  
- The outcome related to the precedent (e.g., upheld, overruled, distinguished, etc.)  
- The context in which the precedent is discussed  

Format your response in structured JSON with keys for "chunk_part", "statutes", and "precedents". If the information spans multiple chunks, note it as a continuation. If no statutes or precedents are mentioned, please indicate "none" for the respective key.  

Response:'''

summarization_prompt = '''You are an advanced AI with specialized capabilities in understanding and analyzing legal documents. Your input consists of a collection of JSON objects that represent key information extracted from various legal cases, encompassing statutes and precedents that are pertinent to Indian law.

Your task is to synthesize this information into a singular, comprehensive JSON object. Please follow these directives as you construct the merged output:
Aggregate entries that pertain to an identical statute or precedent into one consolidated entry, avoiding any duplication.
For every distinct statute or precedent, amass all associated details (such as the case name, citation, legal principles, outcomes, and contextual information) from the disparate JSON objects.
In instances of discordant details, prioritize and preserve the most accurate and complete information, discarding any discrepancies.
Excise any superfluous or non-essential information that does not enhance the comprehension of the case's significance or its standing as a precedent.
Maintain the legal information's integrity at all times, ensuring the precision of citations and the faithful representation of legal doctrines.

The finalized JSON object should function as a streamlined and accessible reference tool for legal professionals, including lawyers and scholars, enabling them to ascertain the relevance and applicability of these cases and statutes for their own legal pursuits.

Please present your response as a solitary JSON object by populating the following template:
{json_obj}

Here are the JSON objects to be refined and amalgamated:
{sc}
 
Consolidated JSON Output:
'''


def add_entry(new_data: str, name: str):
    data = json.loads(new_data)
    precedents = data['precedents']
    statutes = data['statutes']

    connection = psycopg2.connect(
        host="legalscraperserver.postgres.database.azure.com",
        database="postgres",
        user="tejasw",
        password="Password1234",
        port=5432,

    )

    try:
        cursor = connection.cursor()
        insert_query = """
            UPDATE records
            SET precedents = %s, statutes = %s
            WHERE case_name = %s
        """

        data = (json.dumps(precedents), json.dumps(statutes), name)
        cursor.execute(insert_query, data)

        connection.commit()

    except (Exception, psycopg2.Error) as error:
        print("Error while inserting data into PostgreSQL:", error)

    finally:
        cursor.close()


def write(new_data: str):
    with open('statutes_new.json', 'r') as file:
        data = json.load(file)

    data.append(json.loads(new_data))

    with open('statutes_new.json', 'w') as file:
        json.dump(data, file, indent=2)


def get_docs(text):
    text_splitter = RecursiveCharacterTextSplitter.from_tiktoken_encoder(chunk_size=6000,
                                                                         chunk_overlap=600)

    docs = text_splitter.split_text(text)
    docs = [Document(page_content=c) for c in docs]
    return docs


async def process_case(row, llm):
    text = row['pdf_text']
    case_name = row['case_name']
    print(f"Processing {case_name}")
    statutes_tasks = []
    docs = get_docs(text)
    print(len(docs))

    try:
        for i, c in enumerate(docs):
            s = llm.invoke([
                SystemMessage(
                    content='You are an expert paralegal from india who has extensive experience in extracting statutes and precedents.'),
                HumanMessage(content=extraction_prompt.format(
                    i=i, c=c, l=len(docs), metadata=statutes_tasks
                )
                )
            ])
            statutes_tasks.append(s)
        statutes = statutes_tasks
        print(f'Statutes: {statutes}\n---\n')
        sc = [s.content for s in statutes]
        print(f'Statutes: {sc}\n---\n')

        s = llm.invoke([
            SystemMessage(
                content='You are an civil judge from India with extensive experience in Indian law.'),
            HumanMessage(content=summarization_prompt.format(
                sc=sc, json_obj=json_obj))
        ])
        print(f'Summary: {s}\n---\n')
        pattern = r"```([\s\S]*?)```"
        matches = re.findall(pattern, s.content)
        add_entry(matches[0][4:], case_name)
        # write(matches[0][4:])
    except Exception as e:
        print(e)


async def main():
    conn = await asyncpg.connect(host="legalscraperserver.postgres.database.azure.com",
                                 database="postgres",
                                 user="tejasw",
                                 password="Password1234",
                                 port=5432,)
    row = await conn.fetch(
        '''
        SELECT *
        FROM records
        WHERE court_name = 'Supreme Court of India'
        AND precedents is NULL
        ORDER BY TO_DATE(date_of_decision, 'DD-MM-YYYY') DESC;
        ''')

    llm = ChatOpenAI(openai_api_base='http://52.190.47.178:8083/v1',
                     openai_api_key='none',
                     model='Qwen/Qwen1.5-72B-Chat-GPTQ-Int4',
                    # model='Qwen/Qwen1.5-72B-Chat-AWQ',
                     temperature=0.1,
                     )

    for r in row[2:]:
        await process_case(r, llm)
        print('done')

    await conn.close()

asyncio.run(main())
