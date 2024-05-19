import chainlit as cl
from utils.convert import *
from utils.file_processing import *
import warnings
from dotenv import load_dotenv
import os
from openai import AsyncOpenAI
from utils.utils import *
from openai import OpenAI

# XXXXXXX 수정된 부분 -> 필요한 client 불러오기 및 api가져오기
load_dotenv()
API_KEY = os.environ['OPENAI_API_KEY']

client = OpenAI(api_key=API_KEY)
# XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX

@cl.on_chat_start
async def on_chat_start():
    file = await get_file()
    document = get_text(file.path)
    await cl.Message(content=f"`{file.path}` 로딩이 완료되었습니다.").send()

    action = await get_action()
    if action == 'cancel':
        await cl.Message(content=f"다음에 봐요!").send()
    elif action == 'continue':
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

        # save_qa_to_json(Q_list,A_list,"temp.json") # 질문과 답변을 JSON에 저장.

        NA_str = "\n\n".join(NA)

        await cl.Message(content=f"검증이 완료되었습니다. 모델:GPT-4o:\n\n{NA_str}").send()

        '''
        수정된 부분 : txt로 저장
        '''
        await cl.AskActionMessage(
            content="Pick an action!",
            actions=[
                cl.Action(name="t", value="t", label="✅ txt파일로 저장하기"),
            ],
        ).send()

        file_path = "qa_temp.txt"
        file_name = file_path.split('.')[0]

        save_txt(NQ,NA,file_path)

        #좀 더 알아보고 수정할 예정.
        await cl.Message(content=f"Here is your file: [Download {file_name}](upload/{file_path})").send()



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
            cl.Action(name="continue", value="continue", label="💡 퀴즈 만들기"),
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