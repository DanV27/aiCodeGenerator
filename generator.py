import tempfile
import os
import anthropic


#calls antropic API to generate code to print "Hello, World!"
client = anthropic.Anthropic()
message = client.messages.create(
    model="claude-opus-4-6",
    max_tokens=1024,
    messages=[ {"role" : "user", "content": "Act as a code-generating expert. Output only the raw code for printing 'Hello, World!', with no conversational text, explanations, or markdown code blocks"} ]
)
code = message.content[0].text
print(code)

try:
    compile(code, '<string>', 'exec')
    print("The generated code is valid Python.")

    with tempfile.NamedTemporaryFile(delete=True) as named_temp:
        print(f"Writing the generated code to a temporary file: {named_temp.name}")
        named_temp.write(code.encode())


except SyntaxError as e:
    print("The generated code is not valid Python.")
    print(f"SyntaxError: {e}")


