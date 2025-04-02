from litellm import ChatCompletionToolParam, ChatCompletionToolParamFunctionChunk

# FIXME: the descriptuion of the tool needs to be refined
_CHAT_NPC_TOOL_DESCRIPTION = """A messaging tool to chat with people. Use it when you need to interact with someone through messages. You can either interact with a specific person by specifying their name in the tool or set \'name\' to \'all\' if you want to broadcast your message to all the people in the company.

See the description of \'name\' parameter for more details.
""".strip()

ChatNPCTool = ChatCompletionToolParam(
    type='function',
    function=ChatCompletionToolParamFunctionChunk(
        name='chat',
        description=_CHAT_NPC_TOOL_DESCRIPTION,
        parameters={
            'type': 'object',
            'properties': {
                'name': {
                    'type': 'string',
                    'description': 'The name of the user you want to send a message to. Set name to "all" if you want to send your message to all the employees.',
                },
                'message': {
                    'type': 'string',
                    'description': 'The message you want to send to the user.',
                },
            },
            'required': ['name', 'message'],
        },
    ),
)
