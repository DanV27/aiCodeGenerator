import tempfile
import os
import anthropic
import subprocess

def generate_code(spec):
    """Generates code based on the provided specification using the Anthropic API."""
    client = anthropic.Anthropic()
    prompt = f"You are a python code generator. Generate clean, valid python code."
    
    message = client.messages.create(
        model="claude-opus-4-6",
        max_tokens= 2048,
        messages= [{"role": "user", "content": prompt}]
    )

    return message.content[0].text

def extract_code(response_text):
    """Extracts code from the response text."""
    # Assuming the code is enclosed in triple backticks
    import re

    # Try ```python ... ```
    pattern = r"```python\n(.*?)\n```"
    match = re.search(pattern, response_text, re.DOTALL)
    if match:
        return match.group(1).strip()
    
    # Try ``` ... ```
    pattern = r"```\n(.*?)\n```"
    match = re.search(pattern, response_text, re.DOTALL)
    if match:
        return match.group(1).strip()
    
    # Return as-is
    return response_text.strip()

def validate_syntax(code):
    """Validates the syntax of the generated code."""
    try:
        compile(code, '<string>', 'exec')
        return True
    except SyntaxError as e:
        print(f"Syntax error in generated code: {e}")
        return False
    
def run_test(generated_code, test_code, timeout=10):
    """
    Run pytest tests against generated code
    
    Args:
        generated_code: The code you want to test
        test_code: The pytest test code
        timeout: Max time to wait for tests
    
    Returns:
        {
            'passed': True/False,
            'passed_count': int,
            'failed_count': int,
            'total': int,
            'output': str,
            'errors': str
        }
    """
    try:
        # Create a temporary directory to hold the code and tests
        with tempfile.TemporaryDirectory() as tempdir:
            generated_path = os.path.join(tempdir, 'generated.py')
            with open(generated_path, 'w') as f:
                f.write(generated_code)
        
            test_path = os.path.join(tmpdir, 'test_generated.py')
            with open(test_path, 'w') as f:
                f.write(test_code)

            result = subprocess.run(
                ['python', '-m', 'pytest', test_path, '-v'],
                capture_output=True,
                timeout=timeout,
                text=True,
                cwd=tempdir
            )

            output = result.stdout
            errors = result.stderr

            passed_count = output.count(' PASSED')
            failed_count = output.count(' FAILED')
            total = passed_count + failed_count

            return {
                'passed': failed_count == 0 and total > 0,
                'passed_count': passed_count,
                'failed_count': failed_count,
                'total': total,
                'output': output,
                'errors': errors
            }
        
    except subprocess.TimeoutExpired:
        return {
            'passed': False,
            'passed_count': 0,
            'failed_count': 1,
            'total': 1,
            'output': '',
            'errors': f'Test execution timed out after {timeout}s'
        }
    except Exception as e:
        return {
            'passed': False,
            'passed_count': 0,
            'failed_count': 1,
            'total': 1,
            'output': '',
            'errors': f'Error: {str(e)}'
        }
            
#addd fullpipline function!!!!




