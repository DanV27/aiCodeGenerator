import anthropic


#calls antropic API to generate code to print "Hello, World!"
client = anthropic.Anthropic()
message = client.messages.create(
    model="claude-opus-4-6",
    max_tokens=1024,
    messages=[ {"role" : "user", "content": "Python code to print 'Hello, World!'"} ]
)
print(message.content[0].text)
