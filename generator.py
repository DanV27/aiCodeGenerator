import tempfile
import os
import anthropic
import subprocess
#starting from scratrch usiing no help from ai,

def generate_code():
    client = anthropic.Anthropic()
    message = client.messages.create(
        model = "claude-opus-4-6",
        max_tokens = 1024,
        messages = [{"role": "user", "content": "You are a python code generator. Generate clean valid code to print hello world"}]
    )
    print("AINTROPIC RESPONSE: \n", message.content[0].text)
    print("---------------------------------------")
    return(message.content[0].text)


def extract_code (response_text):
    #this will extract code from response
    import re #assuming code will be enclosed in tripple backticks

     # Try ```python ... ```
    pattern = r"```python\n(.*?)\n```"
    code = re.search(pattern, response_text, re.DOTALL)
    if code:
        print('EXTRACTED CODE.....')
        print("PATTERN1: ",code.group(1).strip())
        return code.group(1).strip()

    pattern = r"```\n(.*?)\n```"
    code = re.search(pattern, response_text, re.DOTALL)
    if code:
        print('EXTRACTED CODE.....')
        print("PATTERN2: ",code.group(1).strip())
        return code.group(1).strip()
    

    return(response_text.strip())

response = generate_code()

extract_code(response)

