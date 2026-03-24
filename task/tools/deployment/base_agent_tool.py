import json
from abc import ABC, abstractmethod
from copy import deepcopy
from typing import Any

from aidial_client import AsyncDial
from aidial_sdk.chat_completion import Message, Role, CustomContent, Stage, Attachment
from aidial_sdk.chat_completion.enums import Status
from pydantic import StrictStr

from task.tools.base_tool import BaseTool
from task.tools.models import ToolCallParams, ToolStageConfig
from task.utils.stage import StageProcessor


class BaseAgentTool(BaseTool, ABC):

    def __init__(self, endpoint: str):
        self.endpoint = endpoint

    @property
    @abstractmethod
    def deployment_name(self) -> str:
        pass

    @property
    def stage_config(self) -> ToolStageConfig:
        config = super().stage_config
        config.show_response_in_stage = False
        return config

    async def _execute(self, tool_call_params: ToolCallParams) -> str | Message:
        client = AsyncDial(
            base_url=self.endpoint,
            api_key=tool_call_params.api_key,
            api_version='2025-01-01-preview'
        )

        messages = self._prepare_messages(tool_call_params)

        stream = await client.chat.completions.create(
            deployment_name=self.deployment_name,
            messages=messages,
            stream=True,
            extra_headers={
                "x-conversation-id": tool_call_params.conversation_id,
            },
        )

        content = ''
        custom_content = CustomContent(attachments=[], state=None)
        stages_map: dict[int, Stage] = {}

        async for chunk in stream:
            if not chunk.choices:
                continue
            delta = chunk.choices[0].delta

            if delta.content:
                if tool_call_params.stage:
                    tool_call_params.stage.append_content(delta.content)
                content += delta.content

            if not delta.custom_content:
                continue

            cc_dump = delta.custom_content.model_dump(exclude_none=True)

            if delta.custom_content.attachments:
                for att in delta.custom_content.attachments:
                    sdk_att = Attachment(**att.model_dump(exclude_none=True))
                    if custom_content.attachments is None:
                        custom_content.attachments = []
                    custom_content.attachments.append(sdk_att)
                    tool_call_params.choice.add_attachment(sdk_att)

            if delta.custom_content.state is not None:
                if custom_content.state is None:
                    custom_content.state = {}
                if isinstance(delta.custom_content.state, dict):
                    custom_content.state.update(delta.custom_content.state)

            stages_payload = cc_dump.get("stages")
            if stages_payload:
                for raw in stages_payload:
                    stg = (
                        raw.model_dump(exclude_none=True)
                        if hasattr(raw, "model_dump")
                        else dict(raw)
                    )
                    idx = stg.get("index")
                    if idx is None:
                        continue
                    if idx in stages_map:
                        mirror = stages_map[idx]
                        c = stg.get("content")
                        if c:
                            mirror.append_content(c)
                        for att in stg.get("attachments") or []:
                            if isinstance(att, dict):
                                mirror.add_attachment(**att)
                            else:
                                mirror.add_attachment(**att.model_dump(exclude_none=True))
                        if stg.get("status") == Status.COMPLETED.value:
                            StageProcessor.close_stage_safely(mirror)
                    else:
                        name = stg.get("name")
                        mirror = StageProcessor.open_stage(tool_call_params.choice, name)
                        stages_map[idx] = mirror
                        c = stg.get("content")
                        if c:
                            mirror.append_content(c)
                        for att in stg.get("attachments") or []:
                            if isinstance(att, dict):
                                mirror.add_attachment(**att)
                            else:
                                mirror.add_attachment(**att.model_dump(exclude_none=True))
                        if stg.get("status") == Status.COMPLETED.value:
                            StageProcessor.close_stage_safely(mirror)

        for stage in stages_map.values():
            StageProcessor.close_stage_safely(stage)

        return Message(
            role=Role.TOOL,
            name=StrictStr(self.name),
            tool_call_id=StrictStr(tool_call_params.tool_call.id),
            content=StrictStr(content),
            custom_content=custom_content,
        )

    def _prepare_messages(self, tool_call_params: ToolCallParams) -> list[dict[str, Any]]:
        arguments = json.loads(tool_call_params.tool_call.function.arguments)
        prompt = arguments["prompt"]
        propagate_history = arguments.get("propagate_history", False)

        messages: list[dict[str, Any]] = []

        if propagate_history:
            msgs = tool_call_params.messages
            for i, msg in enumerate(msgs):
                if msg.role != Role.ASSISTANT:
                    continue
                if not msg.custom_content or msg.custom_content.state is None:
                    continue
                state = msg.custom_content.state
                if not isinstance(state, dict):
                    continue
                agent_state = state.get(self.name)
                if not agent_state:
                    continue

                # Add the user message that preceded this assistant turn
                if i > 0:
                    prev = msgs[i - 1]
                    messages.append({
                        "role": prev.role.value if hasattr(prev.role, "value") else str(prev.role),
                        "content": prev.content or "",
                    })

                # Add assistant message with the peer agent's state (not full state)
                copy_msg = deepcopy(msg)
                if copy_msg.custom_content is None:
                    copy_msg.custom_content = CustomContent()
                copy_msg.custom_content.state = agent_state
                row = copy_msg.dict(exclude_none=True)
                row["role"] = msg.role.value if hasattr(msg.role, "value") else str(msg.role)
                messages.append(row)

        custom_content = tool_call_params.messages[-1].custom_content if tool_call_params.messages else None
        messages.append(
            {
                "role": Role.USER.value,
                "content": prompt,
                "custom_content": custom_content.dict(exclude_none=True) if custom_content else None,
            }
        )
        return messages
