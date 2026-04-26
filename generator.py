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



def validate_syntax(code):
    #either colid valid python or api halucinated


    try:
        compile(code, '<string>', 'exec')
        print("✓ Valid Python!")
        return True
    except SyntaxError as e:
        print(f"✗ Syntax error: {e}")
        return False
    
def run_test(generated_code, timeout=10):
    #runs pytest against generated code
    """
    args:
        generated_code: the code you'd like to test
        
        Timeout: max wait time to wait for test
    
    resturns:
        {
            passed: true/false
            passed_count: int
            failed count: int
            total: int
            output: str,
            errors: str
        }
    """

    with tempfile.TemporaryFile(mode='w+') as f:
        f.write(generated_code)
        f.seek(0)
        print('----------------------')
        print("code from Temporary >>>>>")
        print(f"{f.read()}")

        result = subprocess.run(
            ['python', '-m', 'pytest', f, 'v'],
            capture_output= True,
            timeout=timeout,
            text=True,
        )    

        print(result)







response = generate_code()

code = extract_code(response)
validate_syntax(code)
run_test(code)

