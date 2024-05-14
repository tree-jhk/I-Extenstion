class PreprocessingPrompts:
    CorrectPrompt = '''### Extracted Document:
{Extracted_Document}

### Instruction:
The above is a situation where the text is written strangely while reading a file(e.g. .pdf, .pptx, .py, etc).
Rewrite the text above, correcting the errors. (Only write down the rewritten text and not the rest.)

### Response:
'''