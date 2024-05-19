class QuizGeneratorPrompts:

    BasicQuizGeneratorPrompt = '''
Summary of lecture materials: {document}.
The question type is {question_type}.
Be sure to set the difficulty level as {difficulty}
You should ask questions using the words in the lecture material.
Don't ask the concept of this data, don't ask for this data. Don't ask for major concepts in data like below. 
The number of characters per question should not exceed 150.

###BAD EXAMPLE:
What is the name of the lecture?
What is the lecture professor's email?

###ORDER:
질문과 답변은 반드시 한국어로 제시해라
At this time, return questions and answers in json format as follows: (The value consists of a list of 5 questions/answers.)
질문과 답변은 반드시 한국어로 제시해라

{{
    'question':[...],
    'answer':[...]
}}

### Response:
'''