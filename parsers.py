from pygrok import Grok

GROK_LOGIN_EVENT = "%{WORD:eventType}: %{NOTSPACE:date} %{GREEDYDATA:userName} \(%{WORD:playfabId}\) %{GREEDYDATA:eventText}"


def parse_event(event: str, grok_pattern: str) -> tuple[bool, dict[str, str]]:
    pattern = Grok(grok_pattern)
    match = pattern.match(event)
    if not match:
        return (False, match)
    else:
        return (True, match)
