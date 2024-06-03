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

client = OpenAI(api_key=API_KEY) #client는 필요합니다!
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

        save_txt(NQ,NA,file_path)

        # #chainlit에서 사용자에게 다운로드할 수 있게 하는 기능이 없어서. 이건 조금 찾아보는 중입니다...
        # await cl.Message(content=f"Here is your file: [Download {file_name}](upload/{file_path})").send()
        
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