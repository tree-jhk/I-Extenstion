import chainlit as cl
from utils.convert import *
from utils.file_processing import *
import warnings
from dotenv import load_dotenv
import os
from openai import AsyncOpenAI
from utils.utils import *

@cl.on_chat_start
async def on_chat_start():
    file = await get_file()
    document = get_text(file.path)
    await cl.Message(content=f"`{file.path}` 로딩이 완료되었습니다.").send()
    
    action = await get_action()
    if action == 'cancel':
        await cl.Message(content=f"다음에 봐요!").send()
    elif action == 'continue':
        Q, A = await generate_quiz(document)
        await cl.Message(content=f"생성된 질문입니다:\n\n{Q}").send()
        
        await cl.AskActionMessage(
            content="Pick an action!",
            actions=[
                cl.Action(name="continue", value="continue", label="✅ 정답 보기"),
            ],
        ).send()
        
        await cl.Message(content=f"생성된 정답입니다:\n\n{A}").send()

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