import tempfile
import os
import anthropic
import subprocess
import sys
import re
import ast


def generate_code(spec):
    """Generate both code and tests from a user specification"""
    client = anthropic.Anthropic()

    # Generate the code
    code_prompt = f"""You are a python code generator.
Generate clean, valid Python code based on this specification: {spec}
Requirements:
1. Code must be syntactically valid
2. Include proper function signatures with type hints
3. Include docstrings
4. Use typing.Union for type hints (not the | operator) for Python 3.9+ compatibility
Output ONLY the code in a ```python code block, no explanation."""

    message = client.messages.create(
        model="claude-opus-4-6",
        max_tokens=1024,
        messages=[{"role": "user", "content": code_prompt}]
    )
    code = extract_code(message.content[0].text)
    print("✓ Code generated")

    # Generate the tests
    test_prompt = f"""You are a pytest test generator.
Generate pytest tests for this code specification: {spec}
Your tests should:
1. Import the function from the 'generated' module
2. Test normal cases
3. Test edge cases
4. Test error cases
Output ONLY the pytest code in a ```python code block, no explanation."""

    message = client.messages.create(
        model="claude-opus-4-6",
        max_tokens=1024,
        messages=[{"role": "user", "content": test_prompt}]
    )
    test_code = extract_code(message.content[0].text)
    print("✓ Tests generated")

    return code, test_code


def extract_code(response_text):
    """Extract code from markdown code blocks"""
    
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
    
    # Return as-is if no markdown found
    return response_text.strip()


def validate_syntax(code):
    """Check if code is valid Python"""
    try:
        compile(code, '<string>', 'exec')
        print("✓ Syntax valid")
        return True
    except SyntaxError as e:
        print(f"✗ Syntax error: {e}")
        return False


def run_test(generated_code, test_code, timeout=10):
    """Run pytest tests against generated code"""
    try:
        # Create temporary directory
        with tempfile.TemporaryDirectory() as tmpdir:
            # Write code to file
            code_path = os.path.join(tmpdir, 'generated.py')
            with open(code_path, 'w') as f:
                f.write(generated_code)

            # Write tests to file
            test_path = os.path.join(tmpdir, 'test_generated.py')
            with open(test_path, 'w') as f:
                f.write(test_code)
            
            # Run pytest
            result = subprocess.run(
                [sys.executable, '-m', 'pytest', test_path, '-v'],
                capture_output=True,
                timeout=timeout,
                text=True,
                cwd=tmpdir
            )

            #complexity = analyze_complexity(generated_code)

            complexity_data = analyze_complexity(generated_code)

            print('--Complexity analyzed--') #THIS IS NOT WORKING
            print(f"complexity: {complexity_data['cyclomatic_complexity']}, "
                  f"lines: {complexity_data['lines_of_code']}, "
                  f"func: {complexity_data['num_functions']}, "
                  f"names: {complexity_data['function_names']}, "
                  f"Decisions: {complexity_data['decision_points']}")
            
            
            output = result.stdout
            errors = result.stderr
            
            # Count passed/failed
            passed_count = output.count(' PASSED')
            failed_count = output.count(' FAILED')
            total = passed_count + failed_count

            # Print results NEEDS FIXING TOO MUCH ON TERMINAL
            if output:
                print("\nTest Results:")
                print(output)
            
            if errors:
                print("\nErrors:")
                print(errors)
            
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
            'errors': f'Timeout after {timeout}s'
        }
    except Exception as e:
        return {
            'passed': False,
            'passed_count': 0,
            'failed_count': 1,
            'total': 1,
            'output': '',
            'errors': str(e)
        }
    
def analyze_complexity(code):
    #using AST anaylze code complexity

    #Count FUnctions
    tree = ast.parse(code)
    
    functions = [
        node.name for node in ast.walk(tree)
        if isinstance(node, ast.FunctionDef)
    ]
    
    decisions = sum(1 for node in ast.walk(tree)
        if isinstance(node, (ast.If, ast.For, ast.While, ast.ExceptHandler)))
    
    cyclomatic = 1 + decisions

    return { 
            'cyclomatic_complexity': cyclomatic,
            'lines_of_code': len(code.split('\n')),
            'num_functions': len(functions),
            'function_names': functions,
            'decision_points': decisions
        }

def fix_code(code, test_code, test_result):
    """
    Generate a fixed version of the code based on test failures
    
    Returns: fixed_code (string)
    """
    client = anthropic.Anthropic()
    
    # Extract error patterns
    failures = test_result['output']
    
    # Identify the issue
    if "AttributeError" in failures:
        issue = "Type mismatch: code expects objects, tests use dictionaries"
    elif "ImportError" in failures:
        issue = "Missing imports or import errors"
    elif "ValueError" in failures:
        issue = "Logic error: validation too strict"
    elif "TypeError" in failures:
        issue = "Type error: wrong argument types"
    else:
        issue = "Test failure: incompatibility between code and tests"
    
    # Ask Claude to fix
    fix_prompt = f"""The generated code has test failures. Fix it to pass all tests.

    Issue: {issue}

    Original code:
    {code}

    Test failures (first 1000 chars):
    {failures[:1000]}

    Tests:
    {test_code[:500]}

    Requirements:
    1. Fix ONLY the code, not the tests
    2. Keep the same function signatures
    3. Make it compatible with how tests use it
    4. Be conservative - minimal changes"""
    
    message = client.messages.create(
        model="claude-opus-4-6",
        max_tokens=1024,
        messages=[{"role": "user", "content": fix_prompt}]
    )
    
    fixed_code = extract_code(message.content[0].text)
    return fixed_code


def run_pipeline():
    print("="*60)
    print("CODE GENERATION PIPELINE")
    print("="*60)
    
    user_request = input("\nWhat would you like me to code?\n> ")

    # Step 1: Generate
    print("\n[1/4] Generating code and tests...")
    code, test_code = generate_code(user_request)
    
    # Step 2: Display generated code
    print("\n[2/4] Generated code:")
    print("-" * 60)
    print(code)  # ← NO extract_code() call
    print("-" * 60)

    # Step 3: Validate
    print("\n[3/4] Validating syntax...")
    if not validate_syntax(code):
        print("Code is not valid, stopping.")
        exit(1)

    # Step 4: Run tests
    print("\n[4/4] Running tests...")
    result = run_test(code, test_code)
    
    # Print summary
    print("\n" + "="*60)
    if result['passed']:
        print(f"✓ SUCCESS - All {result['total']} tests passed!")
    else:
        print(f"✗ FAILED - {result['failed_count']}/{result['total']} tests failed")
        print("\nAttempting to fix...")
        
        new_code = fix_code(code, test_code, result)
        
        # Validate the fixed code
        if not validate_syntax(new_code):
            print("Fixed code has syntax errors.")
            exit(1)
        
        # Test the fixed code
        new_result = run_test(new_code, test_code)
        
        print("\n" + "="*60)
        if new_result['passed']:
            print(f"✓ SUCCESS AFTER FIX - All {new_result['total']} tests passed!")
            code = new_code  # Use the fixed code
        else: 
            print(f"✗ STILL FAILED - {new_result['failed_count']}/{new_result['total']} tests failed")

    print("="*60)
    return code



# Main execution
if __name__ == "__main__":
    run_pipeline()

    ###MAKE FULL pipline funciton





"""
What 2-3 metrics do you want to track?
-Execution time
-How complex it is (lines of code]

How would you measure if code is "slow"?
-see how long execution time is

What optimizations are most important for your use case?
-Optimizing the big O and execution time

How many times should you retry if an optimization fails?
-Once, if optimization fails lets keep it at that for now

"""




