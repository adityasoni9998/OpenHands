from openhands.events.action import ChatAction

STARTED_SIM: bool = False
SCENARIOS_FILE: str = (
    '/workspace/scenarios.json'  # assumed this is saved inside docker container
)


# async def setup_websocket(self) -> None:
#     """Set up the WebSocket connection with improved error handling"""

#     if self.websocket_url and not self.websocket:
#         retry_count = 0
#         max_retries = 3
#         retry_delay = 1.0

#         while retry_count < max_retries:
#             try:
#                 self.websocket_session = aiohttp.ClientSession()
#                 if self.websocket_session is not None:
#                     # Create a ClientWSTimeout object for the timeout
#                     ws_timeout = ClientWSTimeout(
#                         10.0
#                     )  # Or use named args for specific timeouts
#                     self.websocket = await self.websocket_session.ws_connect(
#                         self.websocket_url,
#                         timeout=ws_timeout,
#                         heartbeat=30.0,  # Keep connection alive
#                     )
#                     logger.info(f'Connected to WebSocket at {self.websocket_url}')
#                     return  # Success, exit the function

#             except aiohttp.ClientConnectorError as e:
#                 logger.error(
#                     f'Connection error (attempt {retry_count+1}/{max_retries}): {e}'
#                 )
#             except aiohttp.WSServerHandshakeError as e:
#                 logger.error(
#                     f'WebSocket handshake error (attempt {retry_count+1}/{max_retries}): {e}'
#                 )
#             except asyncio.TimeoutError:
#                 logger.error(
#                     f'Connection timeout (attempt {retry_count+1}/{max_retries})'
#                 )
#             except Exception as e:
#                 logger.error(
#                     f'Unexpected error connecting to WebSocket (attempt {retry_count+1}/{max_retries}): {e}'
#                 )

#             # Clean up failed session
#             if self.websocket_session and not self.websocket_session.closed:
#                 await self.websocket_session.close()

#             retry_count += 1
#             if retry_count < max_retries:
#                 await asyncio.sleep(retry_delay * retry_count)  # Exponential backoff

#         # All retries failed
#         logger.critical(f'Failed to connect to WebSocket after {max_retries} attempts')
#         self.websocket = None
#         self.websocket_session = None


def start_simulation():
    pass


# assumes that NPC definitions and scenarios have already been pushed to Redis Database via FastAPI
def chat(action: ChatAction):
    # WEBSOCKET_URL = os.environ.get('WEBSOCKET_URL', 'ws://localhost:8080/')

    if not STARTED_SIM:
        start_simulation()
