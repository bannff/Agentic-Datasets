"""S2M Stage: Single-turn to Multi-turn Conversion.

This stage transforms single-turn Q&A pairs into coherent, natural multi-turn conversations
using Strands agents with specialized prompts.

Implementation Status:
- ✅ Infrastructure: Agent config, prompts, error handling
- ⚠️ Agent Integration: Requires strands-agents installation
- 🔴 LLM Calls: Requires model provider authentication

To enable full functionality:
1. Install: pip install strands-agents strands-agents-tools
2. Install provider: pip install boto3 (Bedrock) OR anthropic OR openai
3. Configure credentials (see agents.base.get_provider_setup_instructions)
4. Uncomment the async implementation below
"""

from __future__ import annotations

import json
import logging
from typing import Iterable, Iterator, Optional

from ..schemas.messages import ConversationRecord, Message
from ..agents import (
    AgentConfig,
    create_agent,
    S2M_SYSTEM_PROMPT,
    S2M_USER_TEMPLATE,
    validate_provider_credentials,
)

logger = logging.getLogger(__name__)


class S2MConfig:
    """Configuration for S2M stage."""
    
    def __init__(
        self,
        provider: str = "bedrock",
        model_name: Optional[str] = None,
        temperature: float = 0.7,
        min_turns: int = 3,
        max_turns: int = 5,
        enabled: bool = True,
    ):
        """Initialize S2M configuration.
        
        Args:
            provider: Model provider (bedrock, anthropic, openai)
            model_name: Specific model (uses provider default if None)
            temperature: Generation temperature (0.0-1.0)
            min_turns: Minimum conversation turns to generate
            max_turns: Maximum conversation turns to generate
            enabled: Whether S2M transformation is enabled
        """
        self.provider = provider
        self.model_name = model_name
        self.temperature = temperature
        self.min_turns = min_turns
        self.max_turns = max_turns
        self.enabled = enabled


def s2m(
    records: Iterable[ConversationRecord],
    config: Optional[S2MConfig] = None,
) -> Iterator[ConversationRecord]:
    """Convert single-turn Q&A pairs to multi-turn conversations.
    
    This stage:
    1. Detects single-turn conversations (user Q + assistant A)
    2. Uses Strands agent to generate natural follow-up turns
    3. Maintains context and domain focus across turns
    4. Validates generated conversations
    
    Current Status: PLACEHOLDER
    - Infrastructure ready (config, prompts, validation)
    - Requires strands-agents installation for full functionality
    - Falls back to pass-through if agent not available
    
    Args:
        records: Input conversation records
        config: S2M configuration (uses defaults if None)
    
    Yields:
        Multi-turn conversation records
    """
    config = config or S2MConfig()
    
    if not config.enabled:
        logger.info("S2M stage disabled, passing through")
        yield from records
        return
    
    # Check if Strands SDK is available
    try:
        # NOTE: Uncomment when strands-agents is installed
        # from strands.agents import Agent
        # agent = create_agent(
        #     AgentConfig(
        #         provider=config.provider,
        #         model_name=config.model_name,
        #         temperature=config.temperature,
        #         system_prompt=S2M_SYSTEM_PROMPT,
        #     )
        # )
        # has_agent = agent is not None
        has_agent = False  # Placeholder until SDK installed
    except ImportError:
        logger.warning(
            "Strands SDK not available. Install with: "
            "pip install strands-agents strands-agents-tools"
        )
        has_agent = False
    
    # Validate provider credentials if agent available
    if has_agent and not validate_provider_credentials(config.provider):
        logger.error(
            f"Provider '{config.provider}' credentials not configured. "
            f"See setup instructions in agents.base module."
        )
        has_agent = False
    
    for rec in records:
        # If already multi-turn, yield as-is
        if len(rec.messages) > 2:
            logger.debug(f"Record {rec.id} already multi-turn ({len(rec.messages)} messages)")
            yield rec
            continue
        
        # Check if single-turn Q&A structure
        if len(rec.messages) == 2 and rec.messages[0].role == "user" and rec.messages[1].role == "assistant":
            if has_agent:
                # TODO: Implement async agent call
                # conversation = await _generate_multiturn(rec, agent, config)
                # yield conversation
                logger.warning(f"Agent available but async implementation pending for {rec.id}")
                yield _fallback_multiturn(rec)
            else:
                # Fallback: minimal placeholder
                logger.debug(f"No agent available, using fallback for {rec.id}")
                yield _fallback_multiturn(rec)
        
        elif len(rec.messages) == 1:
            # Single message - add minimal assistant response
            msg = rec.messages[0]
            if msg.role == "user":
                yield ConversationRecord(
                    messages=[
                        msg,
                        Message(
                            role="assistant",
                            content="[Multi-turn conversation would be generated here with Strands agent]"
                        )
                    ],
                    metadata={**(rec.metadata or {}), "stage": "s2m", "generated": "fallback"},
                    source=rec.source,
                    id=rec.id,
                )
            else:
                yield rec
        else:
            # Unknown structure, pass through
            yield rec


def _fallback_multiturn(rec: ConversationRecord) -> ConversationRecord:
    """Fallback multi-turn generation without agent.
    
    Adds a simple follow-up question and answer as a placeholder.
    """
    original_q = rec.messages[0].content
    original_a = rec.messages[1].content
    
    # Simple follow-up
    followup_q = "Can you provide an example?"
    followup_a = "[Example would be provided here with actual agent implementation]"
    
    return ConversationRecord(
        messages=[
            rec.messages[0],  # Original user question
            rec.messages[1],  # Original assistant answer
            Message(role="user", content=followup_q),
            Message(role="assistant", content=followup_a),
        ],
        metadata={
            **(rec.metadata or {}),
            "stage": "s2m",
            "original_turns": 2,
            "generated_turns": 4,
            "generated": "fallback",
        },
        source=rec.source,
        id=rec.id,
    )


# TODO: Implement when strands-agents is installed
# async def _generate_multiturn(
#     rec: ConversationRecord,
#     agent: Any,  # Strands Agent type
#     config: S2MConfig,
# ) -> ConversationRecord:
#     """Generate multi-turn conversation using Strands agent.
#     
#     Args:
#         rec: Input conversation record (single-turn Q&A)
#         agent: Configured Strands agent
#         config: S2M configuration
#     
#     Returns:
#         Multi-turn conversation record
#     """
#     question = rec.messages[0].content
#     answer = rec.messages[1].content
#     
#     # Format prompt
#     prompt = S2M_USER_TEMPLATE.format(
#         question=question,
#         answer=answer
#     )
#     
#     # Generate with agent
#     try:
#         result = await agent.run(prompt)
#         
#         # Parse JSON response
#         messages_data = json.loads(result.content)
#         
#         # Validate message structure
#         messages = []
#         for msg_data in messages_data:
#             if "role" not in msg_data or "content" not in msg_data:
#                 logger.warning(f"Invalid message structure in response: {msg_data}")
#                 continue
#             
#             messages.append(Message(
#                 role=msg_data["role"],
#                 content=msg_data["content"]
#             ))
#         
#         # Validate turn count
#         if len(messages) < config.min_turns:
#             logger.warning(
#                 f"Generated conversation has {len(messages)} turns, "
#                 f"less than minimum {config.min_turns}"
#             )
#         
#         if len(messages) > config.max_turns * 2:  # *2 for user+assistant pairs
#             logger.warning(
#                 f"Generated conversation has {len(messages)} turns, "
#                 f"more than maximum {config.max_turns * 2}"
#             )
#             messages = messages[:config.max_turns * 2]
#         
#         return ConversationRecord(
#             messages=messages,
#             metadata={
#                 **rec.metadata,
#                 "stage": "s2m",
#                 "original_turns": len(rec.messages),
#                 "generated_turns": len(messages),
#                 "provider": config.provider,
#                 "model": config.model_name or "default",
#                 "temperature": config.temperature,
#             },
#             source=rec.source,
#             id=rec.id,
#         )
#     
#     except json.JSONDecodeError as e:
#         logger.error(f"Failed to parse agent response as JSON: {e}")
#         logger.debug(f"Response content: {result.content}")
#         return _fallback_multiturn(rec)
#     
#     except Exception as e:
#         logger.error(f"Error generating multi-turn conversation: {e}")
#         return _fallback_multiturn(rec)

