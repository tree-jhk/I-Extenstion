import chainlit as cl
from utils.convert import *
from utils.file_processing import *
from prompts.quiz_prompts import *
import warnings
from dotenv import load_dotenv
import os
from openai import AsyncOpenAI
from utils.utils import *
from openai import OpenAI
import time

# XXXXXXX 수정된 부분 -> 필요한 client 불러오기 및 api가져오기
load_dotenv()
API_KEY = os.environ['OPENAI_API_KEY']

client = OpenAI(api_key=API_KEY)  # client는 필요합니다!

# XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX

@cl.on_chat_start
async def on_chat_start():
    await start_quiz_workflow()


async def start_quiz_workflow():
    global D
    file = await get_file()
    document = get_text(file.path)
    D = document
    await cl.Message(content=f"`{file.path}` 로딩이 완료되었습니다.").send()

    action = await get_action()
    if action == 'cancel':
        await cl.Message(content=f"다음에 봐요!").send()
    elif action == 'continue':

        await create_quiz(document)


async def create_quiz(document):
    global Q, A
    user_qtype = await get_type()  # 문제유형 설정
    userdiff = await get_diff()  # 난이도 설정
    Q, A = await generate_quiz(document, user_qtype, userdiff)  # get_text로 가져온 텍스트로 generate utils.py에 있음
    await cl.Message(content=f"생성된 질문입니다:\n\n{Q}").send()

    await cl.AskActionMessage(
        content="Pick an action!",
        actions=[
            cl.Action(name="continue", value="continue", label="✅ 정답 보기"),
        ],
    ).send()

    await cl.Message(content=f"생성된 정답입니다:\n\n{A}").send()

    '''
    수정된 부분 : 검증
    '''

    await cl.AskActionMessage(
        content="Pick an action!",
        actions=[
            cl.Action(name="v", value="v", label="✅ 검증하기"),
        ],
    ).send()

    Q_list = Q.split('\n\n')
    A_list = A.split('\n\n')

    NQ, NA = validate_answer(client, Q_list, A_list)

    '''
    JSON FILE처리에 대한 기능은 모두 구현을 해 놨는데(convert.py), QUIZ_CHAT.PY에 추가 하지 않았습니다...
    '''
    # save_qa_to_json(Q_list,A_list) # 질문과 답변을 JSON에 저장.

    NA_str = "\n\n".join(NA)

    await cl.Message(content=f"검증이 완료되었습니다. 모델:GPT-4o:\n\n{NA_str}").send()

    '''
    수정된 부분 : txt로 저장하는 부분
    '''

    await cl.AskActionMessage(
        content="Pick an action!",
        actions=[
            cl.Action(name="t", value="t", label="✅ txt파일로 저장하기"),
        ],
    ).send()

    file_path = "qa_temp.txt"
    file_name = file_path.split('.')[0]

    save_txt(NQ, NA, file_path)

    elements = [
        cl.File(
            name=file_name,
            path=f"./{file_path}",
            display="inline",
        ),
    ]

    await cl.Message(
        content="파일을 다운로드 하세요!", elements=elements
    ).send()

    next_action = await get_next_action()
    if next_action == 'current':
        await create_quiz(document)  # 재귀함수로 구현
    elif next_action == 'new':
        await start_quiz_workflow()  # 처음 파일 받는 부분부터 다시 시작
    elif next_action == 'cancel':
        await cl.Message(content=f"다음에 봐요!").send()
    elif next_action == 'chat':
        await cl.Message(content=f"생성된 퀴즈에 대해 질문을 해주세요!").send()
        

async def get_file():
    files = None
    while files is None:
        files = await cl.AskFileMessage(
            max_size_mb=100,
            content=".mp3, .pptx, .pdf, .txt 파일을 올려주세요.",
            accept={"text/plain": [".txt", ".py"], "application": [".ppt", ".pptx", ".pdf", ".mp3"]},
            raise_on_timeout=False,
        ).send()
    return files[0]


async def get_action():
    res = await cl.AskActionMessage(
        content="Pick an action!",
        actions=[
            cl.Action(name="continue", value="continue", label="📝 퀴즈 만들기"),
            cl.Action(name="cancel", value="cancel", label="❌ 오늘은 그만"),
        ],
    ).send()
    return res['value']


async def get_diff():
    res = await cl.AskActionMessage(
        content="Choose the level of difficulty",
        actions=[
            cl.Action(name="easy", value="easy", label="💡 쉬움"),
            cl.Action(name="normal", value="normal", label="💡💡 보통"),
            cl.Action(name="hard", value="hard", label="💡💡💡💡 어려움"),
        ],
    ).send()
    return res['value']


async def get_type():
    res = await cl.AskActionMessage(
        content="Choose the type of question",
        actions=[
            cl.Action(name="TF", value="TF", label="✅or❌ 참/거짓"),
            cl.Action(name="descriptive", value="descriptive", label="📝 서술형"),
            cl.Action(name="proof", value="proof", label="📝 증명"),
        ],
    ).send()
    return res['value']


# action받아서 끝난 뒤 사용자의 행동 결정
async def get_next_action():
    res = await cl.AskActionMessage(
        content="Choose the next action",
        actions=[
            cl.Action(name="current", value="current", label="🎲 퀴즈 생성하기(현재 파일)"),
            cl.Action(name="new", value="new", label="📁 퀴즈 생성하기(새 파일)"),
            cl.Action(name="cancel", value="cancel", label="❌ 오늘은 그만"),
            cl.Action(name="chat", value="chat", label="💬 채팅 시작하기"),
        ],
    ).send()
    return res['value']

@cl.on_message
async def on_message(user_message):
    global Q, A, D
    user_message = user_message.content
    client = AsyncOpenAI(api_key=os.environ.get(api_key))
    question, answer, document = Q, A, D
    
    prompted = query_intent_prompt.QueryIntentCheckPrompt.format(quiz=question, user_message=user_message)
    check_query_intent = await openai_output_async(client, "gpt-4o", prompted)
    intent = await extract_json(check_query_intent)
    print(f"Intent: {intent['intent']}")
    if intent['intent'] == 1:
        client = AsyncOpenAI(api_key=os.environ.get(api_key))
        await cl.Message(content="GPT-4o가 채점 중입니다...").send()
        msg = cl.Message(content="")
        await msg.send()
        formatted = query_intent_prompt.VerifyAnswerPrompt.format(quiz=question, user_message=user_message, answer=answer)
        print(formatted)
        validate_response = await openai_output_async(client, "gpt-4o", formatted)
        validate_response = await extract_json(validate_response)
        res = '\n'.join(validate_response['result'])
        msg_content = f"채점 결과: {res}"
        await msg.update()
        await cl.Message(content=msg_content).send()
    elif intent['intent'] == 2:
        client = AsyncOpenAI(api_key=os.environ.get(api_key))
        await cl.Message(content="GPT-4o가 답변 중입니다...").send()
        msg = cl.Message(content="")
        await msg.send()
        formatted = query_intent_prompt.AboutQuizPrompt.format(document=document, quiz=question, user_message=user_message, answer=answer)
        print(formatted)
        validate_response = await openai_output_async(client, "gpt-4o", formatted)
        msg_content = f"{validate_response}"
        await msg.update()
        await cl.Message(content=msg_content).send()
    elif intent['intent'] == 3:
        await cl.Message(content="퀴즈를 종료합니다! 종료될 때까지 잠시만 기다려주세요! \n\n 😃 다음에 또 봐요! 😃").send()
        exit(0)
    elif intent['intent'] == 4:
        await cl.Message(content="퀴즈를 재시작합니다!").send()
        await create_quiz(document)
    elif intent['intent'] == 5:
        await cl.Message(content="😥 프롬프트 출력은 금지되어 있습니다. 😥").send()
    elif intent['intent'] == 6:
        client = AsyncOpenAI(api_key=os.environ.get(api_key))
        await cl.Message(content="GPT-4o가 답변 중입니다...").send()
        msg = cl.Message(content="")
        await msg.send()
        formatted = query_intent_prompt.SimpleQuizPrompt.format(user_message=user_message)
        print(formatted)
        response = await openai_output_async(client, "gpt-4o", formatted)
        msg_content = f"{response}"
        await msg.update()
        await cl.Message(content=msg_content).send()
    
    await cl.Message(content="😃 질문 또 해주세요! 😃").send()