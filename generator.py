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
    print(message.content)

generate_code()