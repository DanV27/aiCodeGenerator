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
    
def run_simple_test(generated_code, timeout=10):
    """
    Simple version: just run the code and see if it executes
    
    For "Hello World" testing
    """
    try:
        # Create temporary directory
        with tempfile.TemporaryDirectory() as tmpdir:
            # Write code to a file
            code_path = os.path.join(tmpdir, 'generated.py')
            with open(code_path, 'w') as f:
                f.write(generated_code)
            
            print(f"\n--- Running code from {code_path} ---")
            
            # Execute the code
            result = subprocess.run(
                ['python3', code_path],
                capture_output=True,
                timeout=timeout,
                text=True
            )
            
            print(f"Output: {result.stdout}")
            if result.stderr:
                print(f"Errors: {result.stderr}")
            
            # Check if it ran successfully (exit code 0)
            if result.returncode == 0:
                print("✓ Code executed successfully!")
                return {
                    'passed': True,
                    'output': result.stdout,
                    'errors': result.stderr
                }
            else:
                print("✗ Code execution failed!")
                return {
                    'passed': False,
                    'output': result.stdout,
                    'errors': result.stderr
                }
    
    except subprocess.TimeoutExpired:
        print(f"✗ Code execution timed out after {timeout}s")
        return {
            'passed': False,
            'output': '',
            'errors': f'Timeout after {timeout}s'
        }
    except Exception as e:
        print(f"✗ Error: {e}")
        return {
            'passed': False,
            'output': '',
            'errors': str(e)
        }


# Main execution
if __name__ == "__main__":
    print("="*50)
    print("HELLO WORLD TEST")
    print("="*50)
    
    # Step 1: Generate
    print("\n[1/3] Generating code...")
    response = generate_code()
    
    # Step 2: Extract
    print("\n[2/3] Extracting code...")
    code = extract_code(response)
    
    # Step 3: Validate
    print("\n[3/3] Validating syntax...")
    if not validate_syntax(code):
        print("Code is not valid, stopping.")
        exit(1)
    
    # Step 4: Run
    print("\n[4/4] Running code...")
    result = run_simple_test(code)
    
    # Print summary
    print("\n" + "="*50)
    if result['passed']:
        print("✓ SUCCESS - Code executed without errors!")
    else:
        print("✗ FAILED - Code execution failed")
    print("="*50)




