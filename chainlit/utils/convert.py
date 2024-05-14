from PyPDF2 import PdfReader
import re
import pptx

def extract_text_from_pdf(pdf_file_path):
    text = ""
    with open(pdf_file_path, "rb") as f:
        reader = PdfReader(f)
        for page in reader.pages:
            text += page.extract_text()
    return text

def file2text(file,client=None):
    print(file)
    if re.search(r'\.mp3$',file): #mp3 -> string
        audio_file = open(file, "rb")
        transcription = client.audio.transcriptions.create(
            model="whisper-1",
            file=audio_file
        )
        return transcription.text

    elif re.search(r'\.pdf$',file): #pdf -> string
        text = ""
        with open(file, "rb") as f:
            reader = PdfReader(f)
            for page in reader.pages:
                text += page.extract_text()
        return text

    elif re.search(r'\.ppt$',file) or re.search(r'\.pptx$',file): #ppt -> string
        text = ""
        presentation = pptx.Presentation(file)
        for slide in presentation.slides:
            for shape in slide.shapes:
                if shape.has_text_frame:
                    text_frame = shape.text_frame
                    for paragraph in text_frame.paragraphs:
                        for run in paragraph.runs:
                            text += run.text
        return text

    else: #txt -> string
        try:
            with open(file, 'r', encoding='utf-8') as file:
                text = file.read()
            return text
        except FileNotFoundError:
            print("파일을 찾을 수 없습니다.")
            return None
        except Exception as e:
            print("오류 발생:", e)
            return None

def response(client,a_id,t_id,content,command):
  message = client.beta.threads.messages.create(
    thread_id=t_id,
    role="user",
    content=content
  )


  run = client.beta.threads.runs.create_and_poll(
    thread_id=t_id,
    assistant_id=a_id,
    instructions=command
  )

  if run.status == 'completed':
    messages = client.beta.threads.messages.list(
      thread_id=t_id
    )
    return str(messages.data[0].content[0].text.value)
  else:
    return None

def respoens2(client,model,data,query,temperature=1,max_tokens=1500):
    response = client.chat.completions.create(
        model=model,
        messages=[
            {
                "role": "user",
                "content": data
            },
            {
                "role": "assistant",
                "content": query
            }

        ],
        temperature=temperature,
        max_tokens=max_tokens,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0
    )
    return response.choices[0].message.content


# def get_style(file):
#     x = extract_text_from_pdf(file)
#     return '<<'+"시험문제는 다음과 같이 나온다."+x+"이러한 문제의 유형을 대비해야한다."+'>>'


def content_preprocessing(client,as_id,t_id,file,style=None):

    if re.search(r'\.mp3$',file):

        audio_file = open(file, "rb")
        transcription = client.audio.transcriptions.create(
            model="whisper-1",
            file=audio_file
        )
        pdf_text = transcription.text
    else:
        pdf_text = extract_text_from_pdf(file)

    x = len(pdf_text)
    num1 = x // 4
    num2 = x // 2
    num3 = int(x * (3/4))
    pdf_1 = '<<'+pdf_text[0:num1]+'>>'
    pdf_2 = '<<'+pdf_text[num1:num2]+'>>'
    pdf_3 = '<<'+pdf_text[num2:num3]+'>>'
    pdf_4 = '<<'+pdf_text[num3:x-1]+'>>'


    # if style != None:
    #     command1 = style+"이를 참고하여 <* *>안에 있는 내용을 바탕으로 워드 한 페이지 분량의 교재를 만들어라. "
    #
    # x = response(client,as_id,t_id,pdf_1,st+"이를 참고하여 <* *>안에 있는 내용을 바탕으로 워드 한페이지 분량의 교재를 만들어라.")
    # print(x)

    command1 = "이를 참고하여 << >>안에 있는 내용을 바탕으로 워드 한페이지 분량의 교재를 만들어라. 내용은 정확하고 자세해야 한다."
    chunk1 = response(client,as_id,t_id,pdf_1,command1)
    chunk2 = response(client, as_id, t_id, pdf_2, command1)
    chunk3 = response(client, as_id, t_id, pdf_3, command1)
    chunk4 = response(client, as_id, t_id, pdf_4, command1)
    enter_str = "\n\n"

    re_str = chunk1+enter_str+chunk2+enter_str+chunk3+enter_str+chunk4

    return re_str

def content_preprocessing2(client,file,style=None):
    model = "gpt-3.5-turbo"

    pdf_text = file2text(file,client) #ppt,mp3,txt,pdf -> string으로 return

    x = len(pdf_text)
    num1 = x // 4
    num2 = x // 2
    num3 = int(x * (3/4))
    pdf_1 = '<<'+pdf_text[0:num1]+'>>'
    pdf_2 = '<<'+pdf_text[num1:num2]+'>>'
    pdf_3 = '<<'+pdf_text[num2:num3]+'>>'
    pdf_4 = '<<'+pdf_text[num3:x-1]+'>>'

    command1 = "이를 참고하여 << >>안에 있는 내용을 바탕으로 워드 한페이지 분량의 교재를 만들어라. 내용은 정확하고 자세해야 한다."

    chunk1 = respoens2(client,model,pdf_1,command1)
    chunk2 = respoens2(client,model,pdf_2,command1)
    chunk3 = respoens2(client,model,pdf_3,command1)
    chunk4 = respoens2(client,model,pdf_4,command1)
    enter_str = "\n\n"

    re_str = chunk1+enter_str+chunk2+enter_str+chunk3+enter_str+chunk4

    return re_str

