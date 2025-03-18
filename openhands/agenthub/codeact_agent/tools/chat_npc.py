from litellm import ChatCompletionToolParam, ChatCompletionToolParamFunctionChunk

_CHAT_NPC_TOOL_DESCRIPTION = """Chat with users described in the task using messages. Use it when you need to interact with someone through messages.

See the description of "code" parameter for more details.
"""

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
                    'description': 'The name of the user you want to interact with.',
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
