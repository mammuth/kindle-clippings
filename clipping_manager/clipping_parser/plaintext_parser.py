from typing import Union, Dict, List

from httpagentparser import detect

def get_clips_from_text(content: Union[str, bytes], http_agent: str) -> List[str]:
    if isinstance(content, bytes):
        content = content.decode('utf-8')

    user_os_name = detect(http_agent)['os']['name']
    eol_seperator = '\r\n' if user_os_name == 'Windows' else '\n\n'

    clips = [c.strip() for c in content.split(eol_seperator*2) if c.strip() != '']
    return clips
