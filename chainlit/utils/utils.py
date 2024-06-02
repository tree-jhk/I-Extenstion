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
import openai
<<<<<<< HEAD
#from convert import *
max_tokens = 4096
=======
>>>>>>> d334eb7ed11d8ab29e10fcda3050ffd9a279a3d5

warnings.filterwarnings('ignore')
load_dotenv()  # .env 파일 로드

api_key = os.getenv('OPENAI_API_KEY')  # 환경 변수 읽기
os.environ["OPENAI_API_KEY"] = api_key

model = 'gpt-4o' #기존 : gpt-3.5-turbo
better_model = 'gpt-4-turbo'
client = AsyncOpenAI(api_key=os.environ.get(api_key))

API_MAX_RETRY = 16
API_RETRY_SLEEP = 1
API_ERROR_OUTPUT = "$ERROR$"


def openai_api_messages(prompt, status='user', chat_history=list()):
    if status == 'user':
        next_chat = [{"role": "user", "content": prompt}]
    elif status == 'system':
        next_chat = [{"role": "system", "content": prompt}]
    chat_history.extend(next_chat)
    return chat_history

async def openai_output_async(client, model, query, chat_history=list()):
    global max_tokens
    openai_input = openai_api_messages(query, chat_history=chat_history)
    model = model
    output = API_ERROR_OUTPUT
    for _ in range(API_MAX_RETRY):
        response = await client.chat.completions.create(
            model=model,
            messages=openai_input,
            max_tokens=max_tokens,
            n=1,
            temperature=0,
        )
        output = response.choices[0].message.content
        break
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


def set_diff(userdiff): # ###ORDER
    if userdiff == 'easy':
        diff = """
Difficulty level that requires basic conceptual understanding and memorization.
Make sure the questions are at a level you can solve if you've read the material.
"""
    elif userdiff == 'normal':
        diff = """
If you read this material once and understand it, ask questions with a difficulty that you can think about and solve.
Apply the concept and ask questions that need to be analyzed
"""
    elif userdiff == 'hard':
        diff = """
Read this material over and over again two or three times and ask questions about concepts that you might not have caught even if you understand all the contents. Questions about concepts that come out relatively less frequently are also good.
Read this material 2 or 3 times repeatedly, and even if you understand it, it's hard to calculate, so it's a difficult question to solve
Ask questions that need to be able to solve complex problems
"""
    return diff


def set_qtype(user_qtype):  # 함수가 실행되는동안 다른것도 실행됨
    if user_qtype == 'TF':
        q_type = """ 
Create a problem type that distinguishes true or false for a given sentence.
The answer to the given question must be yes or no.
Ask questions that distinguish true lies for the given view.
질문과 답변은 반드시 한국어로 제시해라

###EXAMPLE:
1) Array is a static data structure because it cannot grow or shrink during program execution (T/F)
(2) A singly linked list is a concrete data structure consisting of a sequence of nodes, starting
from a head pointer   (T/F)
(3) Singly Linked List의 노드는 자신의 이전 노드를 알 수 없다 (T/F)
"""
    elif user_qtype == 'descriptive':
        q_type = """
###ORDER:
create a descriptive problems  
서술형으로 문제를 만들어
###Guidelines:
Use prompts that encourage exploration
Leave room for interpretation
Emphasize the process over the product
질문과 답변은 한국어로 제시해라
###EXAMPLE:
1. In what cases do you think artificial intelligence technology can cause ethical issues? How do you think we should respond to these cases?
2. Imagine you are a urban planner tasked with designing a sustainable transportation system for a rapidly growing city. What would be your top three priorities, and how would you implement them to minimize environmental impact while ensuring efficient travel for citizens?
3. Explain why we cannot design an algorithm for a breadth-first traversal using a stack. You are required to explain your thought with some examples.
4. Describe the procedure for deleting an element from a 2-4 tree. Explain how the tree rebalances itself after a deletion to maintain its properties. Include an example to demonstrate the deletion process and the necessary rebalancing steps.
5. Explain the process of inserting a new element into a 2-4 tree. Describe how the tree maintains its balanced property during insertion. Provide an example with a sequence of insertions and illustrate each step of the process.
6. Prove that the height of a 2-4 tree with n elements is O(logn). Explain why the height of the tree is logarithmic in the number of elements and discuss the implications of this property on search operations.
"""
    elif user_qtype == 'proof':
        q_type = """
###ORDER:
Create a problem that must be logically solved to see which proposition is true or false
Create a problem that proves about an axiom
###Guidelines:
Be explicit about the task: Clearly state that you want the model to prove a mathematical statement or theorem. You can use phrases like "증명하시오", "~임을 보여라", or "이 명제가 참임을 보여라".
Provide necessary context and definitions: ex) efdinitions, formulas, and assumptions
###Example:
For a tree T, let nI denote the number of its internal nodes, and let nE denote the number of its external nodes. Show that if every internal node in T has exactly 3 children, then nE = 2nI + 1.
Show that (n + 1)^5 is O(n^5)
In a red-black tree, the black height is the number of black nodes encountered on the path from the root to that node. On a path from the root to a leaf (a leaf is considered a NIL node), all paths have the same black height. Design an algorithm to find the black height of each node in a red-black tree, and prove that your algorithm is correct.
A hash table is a data structure that stores key-value pairs, where the key is entered into a hash function to determine the index in which the value will be stored. The average search time for a hash table can vary depending on how collisions are resolved. In a hash table using chaining, n keys to Prove the average search time when hashing n keys into m slots.
Design an algorithm to count the number of nodes in a Singly Linked List and prove that it works correctly.
Prove that the total number of nodes in a Complete Binary Tree of height h is 2^(h+1) -1.

"""
    return q_type


async def generate_quiz(document, user_qtype, userdiff):
    # CorrectPrompted_document = PreprocessingPrompts.CorrectPrompt.format(Extracted_Document=document)  # 파일 요약본에서 오탈자 수정
    # Corrected_document = await openai_output_async(client=client, model=model,
    #                                                query=CorrectPrompted_document)  # await한 이유 --> async로 따로 돌아가는 상황인데 결과값이 꼭 필요한
    diff = set_diff(userdiff)
    q_type = set_qtype(user_qtype)
    QuesionAnswerPrompted_document = QuizGeneratorPrompts.BasicQuizGeneratorPrompt.format(document=document,
                                                                                          question_type=q_type,
                                                                                          difficulty=diff)  # QuesionAnswePrompted_document에는 기본 내용 + 오탈자 교정된 요약본이 들어감
    #print(QuesionAnswerPrompted_document)
    QuesionAnswerJson = await openai_output_async(client=client, model=model, query=QuesionAnswerPrompted_document)
    QuesionAnswerJson = await extract_json(QuesionAnswerJson)
    question, answer = QuesionAnswerJson['question'], QuesionAnswerJson['answer']
    Q, A = '\n\n'.join(question), '\n\n'.join(answer)

    return Q, A







