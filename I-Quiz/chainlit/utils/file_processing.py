import os
from utils.convert import *

def get_text(file_dir):
    available_extensions = ['ppt', 'txt', 'pdf', 'pptx', 'mp3']
    file_extension = file_dir.split('.')[-1]
    if file_extension in available_extensions:
        document = file2text(file_dir)

        return document
    else:
        raise Exception("해당 확장자를 가진 파일은 현재 지원하지 않습니다.")