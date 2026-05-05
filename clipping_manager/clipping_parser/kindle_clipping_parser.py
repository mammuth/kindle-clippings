# -*- coding: utf-8 -*-
"""
Some methods are taken from https://github.com/lxyu/kindle-clippings
Modifications have been made.
"""

import collections
import re
from typing import List, Dict, Union

BOUNDARY = u"==========\r\n"


def _get_sections(file_content: str):
    content = file_content.replace(u'\ufeff', u'')
    if BOUNDARY in content:
        return content.split(BOUNDARY)

    # Fallback: split Kindle section boundaries with any newline style.
    return re.split(r'={10}\s*(?:\r\n|\n|\r)', content)


def _get_clip(section: str) -> Union[None, Dict[str, Union[str, int]]]:
# def _get_clip(section: str):
    clip = {}

    lines = [l.strip() for l in section.splitlines() if l.strip()]
    if len(lines) < 3:
        return None

    clip['book'] = lines[0]
    # Kindle location range, e.g. "location 123-124".
    match = re.search(r'(\d+)\s*-\s*\d+', lines[1])
    if not match:
        # Kindle page format, e.g. "on page 40".
        match = re.search(r'\bpage\s+(\d+)\b', lines[1], re.IGNORECASE)
    if not match:
        return None
    position = match.group(1)

    clip['position'] = int(position)
    clip['content'] = '\n'.join(lines[2:])

    return clip


def get_clips_from_text(content: Union[str, bytes]) -> Dict[str, List]:
    if isinstance(content, bytes):
        content = content.decode('utf-8')

    sections = _get_sections(content)

    clips = collections.defaultdict(list)
    for section in sections:
        clip = _get_clip(section)
        if clip:
            clips[clip['book']].append(clip['content'])

    # remove key with empty value
    clips = {k: v for k, v in clips.items() if v}

    return clips


def get_clips_from_file(filename: str) -> Dict[str, List]:
    with open(filename, 'rb') as f:
        content = f.read().decode('utf-8')
    return get_clips_from_text(content)


if __name__ == '__main__':
    clippings = get_clips_from_file(u'My Clippings.txt')
    print(clippings)
