from litellm import ChatCompletionToolParam, ChatCompletionToolParamFunctionChunk

# FIXME: the descriptuion of the tool needs to be refined
_CHAT_NPC_TOOL_DESCRIPTION = """A tool to communicating with people via text messages. Use it when you need to interact with a person. You can either interact with a specific person by specifying their name in the tool or set \'name\' to \'all\' if you want to send your message to all the people.

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
                    'description': 'The name of the person you want to send your message to. Set \'name\' to "all" ONLY if you want to send your message on the general channel to all the users. Note that this parameter is case-sensitive.',
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
