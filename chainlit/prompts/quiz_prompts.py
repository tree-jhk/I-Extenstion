class QuizGeneratorPrompts:
    BasicQuizGeneratorPrompt = '''### Document:
{document}

### Instruction:
Create 10 questions based on the above document and provide answers to the questions. (질문과 답변은 한국어로 제공해라)
At this time, return questions and answers in json format as follows: (The value consists of a list of 10 questions/answers.)

{{
    'question':[...],
    'answer':[...]
}}

### Response:
'''