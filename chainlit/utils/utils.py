import time
import json
import re
from prompts.preprocessing_prompts import *
from prompts.quiz_prompts import *
from async_debug.async_debug import *
import warnings
from dotenv import load_dotenv
import os
from openai import AsyncOpenAI

warnings.filterwarnings('ignore')
load_dotenv()  # .env 파일 로드

api_key = os.getenv('OPENAI_API_KEY')  # 환경 변수 읽기
os.environ["OPENAI_API_KEY"] = api_key

model = 'gpt-3.5-turbo'
better_model = 'gpt-4-turbo'
client = AsyncOpenAI(api_key=os.environ.get(api_key))

API_MAX_RETRY = 16
API_RETRY_SLEEP = 10
API_ERROR_OUTPUT = "$ERROR$"

def openai_api_messages(prompt, status='user', chat_history=list()):
    if status == 'user':
        next_chat = [{"role": "user", "content": prompt}]
    elif status == 'system':
        next_chat = [{"role": "system", "content": prompt}]
    chat_history.extend(next_chat)
    return chat_history

async def openai_output_async(client, model, query, chat_history=list()):
    openai_input = openai_api_messages(query, chat_history=chat_history)
    model = model
    output = API_ERROR_OUTPUT
    for _ in range(API_MAX_RETRY):
        try:
            response = await client.chat.completions.create(
                model=model,
                messages=openai_input,
                n=1,
                temperature=0,
            )
            output = response.choices[0].message.content
            break
        except:
            print("ERROR DURING OPENAI API")
            time.sleep(API_RETRY_SLEEP)
    return output

async def extract_json(text):
    match = re.search(r'\{.*?\}', text, re.S)

    if match:
        json_content = match.group(0)
        try:
            data = json.loads(json_content.replace("'", '"'))
            return data
        except json.JSONDecodeError as e:
            fixed_json = re.sub(r',\s*\}', '}', re.sub(r',\s*\]', ']', json_content))
            try:
                data = json.loads(fixed_json)
                return data
            except json.JSONDecodeError as e:
                print(f"Failed to decode JSON again: {e}")
                return None
    else:
        print("No JSON found in the response text.")
        return None

async def generate_quiz(document):
    CorrectPrompted_document = PreprocessingPrompts.CorrectPrompt.format(Extracted_Document=document)
    Corrected_document = await openai_output_async(client=client, model=model, query=CorrectPrompted_document)
    
    QuesionAnswerPrompted_document = QuizGeneratorPrompts.BasicQuizGeneratorPrompt.format(document=Corrected_document)
    QuesionAnswerJson = await openai_output_async(client=client, model=model, query=QuesionAnswerPrompted_document)
    QuesionAnswerJson = await extract_json(QuesionAnswerJson)
    
    question, answer = QuesionAnswerJson['question'], QuesionAnswerJson['answer']
    Q, A = '\n\n'.join(question), '\n\n'.join(answer)
    
    return Q, A