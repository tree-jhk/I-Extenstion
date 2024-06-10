import chainlit as cl
from utils.convert import *
from utils.file_processing import *
from prompts.quiz_prompts import validate_user_answer
import warnings
from dotenv import load_dotenv
import os
from openai import AsyncOpenAI
from utils.utils import *
from openai import OpenAI

# XXXXXXX 수정된 부분 -> 필요한 client 불러오기 및 api가져오기
load_dotenv()
API_KEY = os.environ['OPENAI_API_KEY']

client = OpenAI(api_key=API_KEY)  # client는 필요합니다!

user_request = ''

@cl.on_chat_start
async def on_chat_start():
    await cl.Message(content="안녕하세요! I-Quiz에 오신 것을 환영합니다!").send()
    await start_quiz_workflow()

async def start_quiz_workflow():
    file = await get_file()
    document = get_text(file.path)
    await cl.Message(content=f"`{file.path}` 로딩이 완료되었습니다.").send()

    action = await get_action()
    if action == 'cancel':
        await cl.Message(content=f"다음에 봐요!").send()
    elif action == 'continue':
        await create_quiz(document)

@cl.on_message
async def on_message(input_message):
    if user_request == ''

@cl.on_message
async def on_message(user_answer):
    global Q, A
    question, answer = Q, A
    await cl.Message(content="GPT-4o가 채점 중입니다...").send()
    msg = cl.Message(content="")
    await msg.send()
    formatted = validate_user_answer.ValidateUserAnswer.format(user_answer=user_answer, question=question, answer=answer)
    validate_response = await openai_output_async(client, model, formatted)
    msg_content = f"채점 결과: {validate_response}"
    await msg.update()

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
        ],
    ).send()
    return res['value']