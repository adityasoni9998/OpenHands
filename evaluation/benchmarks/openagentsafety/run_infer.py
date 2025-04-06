# This file is a hack to deterministically test the chat-npc tool by running it inside the OpenHands docker runtime

import functools
import os

import pandas as pd

from evaluation.utils.shared import (
    EvalMetadata,
    EvalOutput,
    codeact_user_response,
    get_default_sandbox_config_for_eval,
    make_metadata,
)
from openhands.core.config import (
    AppConfig,
    get_llm_config_arg,
    get_parser,
)
from openhands.core.config.utils import get_agent_config_arg
from openhands.core.logger import openhands_logger as logger
from openhands.core.main import create_runtime
from openhands.events.action import ChatAction, CmdRunAction
from openhands.events.observation import CmdOutputObservation
from openhands.runtime.base import Runtime
from openhands.utils.async_utils import call_async_from_sync

DATASET_CACHE_DIR = os.path.join(os.path.dirname(__file__), 'data')


AGENT_CLS_TO_FAKE_USER_RESPONSE_FN = {
    'CodeActAgent': functools.partial(codeact_user_response, encapsulate_solution=True),
}

AGENT_CLS_TO_INST_SUFFIX = {
    'CodeActAgent': 'When you think you have solved the question, please first send your answer to user through message and then exit.\n'
}


def get_config(
    metadata: EvalMetadata,
) -> AppConfig:
    sandbox_config = get_default_sandbox_config_for_eval()
    sandbox_config.base_container_image = 'python:3.12-bookworm'
    config = AppConfig(
        default_agent=metadata.agent_class,
        run_as_openhands=False,
        runtime='docker',
        max_iterations=metadata.max_iterations,
        sandbox=sandbox_config,
        # do not mount workspace
        workspace_base=None,
        workspace_mount_path=None,
    )
    config.set_llm_config(metadata.llm_config)
    if metadata.agent_config:
        config.set_agent_config(metadata.agent_config, metadata.agent_class)
    else:
        logger.info('Agent config not provided, using default settings')
        agent_config = config.get_agent_config(metadata.agent_class)
        agent_config.enable_prompt_extensions = False
        agent_config.enable_chat_tool = True
    return config


def initialize_runtime(runtime: Runtime):
    """Initialize the runtime for the agent.

    This function is called before the runtime is used to run the agent.
    """
    logger.info(f"{'-' * 50} BEGIN Runtime Initialization Fn {'-' * 50}")
    obs: CmdOutputObservation

    action = CmdRunAction(command='mkdir -p /workspace')
    logger.info(action, extra={'msg_type': 'ACTION'})
    obs = runtime.run_action(action)
    src_file = os.path.join(
        os.getcwd(), 'evaluation/benchmarks/openagentsafety/scenarios.json'
    )
    assert os.path.exists(src_file)
    dest_file = os.path.join('/workspace', 'scenarios.json')
    runtime.copy_to(src_file, dest_file)
    assert obs.exit_code == 0

    action = ChatAction(
        content='Hi Li! Please provide feedback for the meeting.', npc_name='Li'
    )
    obs = runtime.run_action(action)
    print(obs)


def process_instance(
    instance: pd.Series,
    metadata: EvalMetadata,
    reset_logger: bool = True,
) -> EvalOutput:
    pass


if __name__ == '__main__':
    parser = get_parser()
    parser.add_argument(
        '--data-split',
        type=str,
        help='data split to evaluate, eg. test',
        default='validation',
    )
    args, _ = parser.parse_known_args()

    agent_config = None
    if args.agent_config:
        agent_config = get_agent_config_arg(args.agent_config)

    llm_config = None
    if args.llm_config:
        llm_config = get_llm_config_arg(args.llm_config)
        # modify_params must be False for evaluation purpose, for reproducibility and accurancy of results
        llm_config.modify_params = False

    if llm_config is None:
        raise ValueError(f'Could not find LLM config: --llm_config {args.llm_config}')

    metadata = make_metadata(
        llm_config=llm_config,
        dataset_name='openagentsafety',
        agent_class=args.agent_cls,
        max_iterations=args.max_iterations,
        eval_note=args.eval_note,
        eval_output_dir=args.eval_output_dir,
        data_split=args.data_split,
        agent_config=agent_config,
    )
    config = get_config(metadata=metadata)
    runtime = create_runtime(config)
    call_async_from_sync(runtime.connect)
    initialize_runtime(runtime)
