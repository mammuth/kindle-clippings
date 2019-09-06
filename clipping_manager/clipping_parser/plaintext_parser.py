from typing import Union, Dict, List


def get_clips_from_text(content: Union[str, bytes]) -> List[str]:
    if isinstance(content, bytes):
        content = content.decode('utf-8')

    clips = [c.strip() for c in content.split('\n\n') if c.strip() != '']
    return clips
