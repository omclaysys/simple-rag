"""State definition for the Personal Task Assistant."""

from langgraph.graph import MessagesState


class TaskAssistantState(MessagesState):
    """Extended state for the task assistant.

    Inherits:
        messages: list of messages with add_messages reducer for history.

    Additional fields:
        user_input: The latest raw user query.
        current_date_time: ISO-like string injected for prompt context.
    """

    user_input: str
    current_date_time: str
