from datetime import datetime
from pygrok import Grok

GROK_LOGIN_EVENT = "%{WORD:eventType}: %{NOTSPACE:date}: %{GREEDYDATA:userName} \(%{WORD:playfabId}\) logged %{WORD:order}"
MORDHAU_DATE_FORMAT = "%Y.%m.%d-%H.%M.%S"
GROK_CHAT_EVENT = "%{WORD:eventType}: %{NOTSPACE:playfabId}, %{GREEDYDATA:userName}, \(%{WORD:channel}\) %{GREEDYDATA:message}"


def parse_event(event: str, grok_pattern: str) -> tuple[bool, dict[str, str]]:
    pattern = Grok(grok_pattern)
    match = pattern.match(event)
    if not match:
        return (False, match)
    else:
        return (True, match)


def parse_date(date_str: str) -> datetime:
    return datetime.strptime(date_str, MORDHAU_DATE_FORMAT)
