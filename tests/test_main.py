# octo-cl/tests/test_main.py

import pytest
from octo_cl.main import parse_tool_calls

def test_parse_single_tool_call():
    text = '<tool_call:read_file path="foo.py" />'
    calls = parse_tool_calls(text)
    
    assert len(calls) == 1
    assert calls[0]['name'] == 'read_file'
    assert calls[0]['params']['path'] == 'foo.py'

def test_parse_content_tool_call():
    text = '<tool_call:write_file path="hello.txt">Hello World!</tool_call:write_file>'
    calls = parse_tool_calls(text)
    
    assert len(calls) == 1
    assert calls[0]['name'] == 'write_file'
    assert calls[0]['params']['path'] == 'hello.txt'
    assert calls[0]['params']['content'] == 'Hello World!'

def test_parse_multiple_tool_calls():
    text = (
        'Let me check the files first.
'
        '<tool_call:list_files path="src" />
'
        'Now I will write a new file.
'
        '<tool_call:write_file path="src/new.py">print("new")</tool_call:write_file>'
    )
    calls = parse_tool_calls(text)
    
    assert len(calls) == 2
    assert calls[0]['name'] == 'list_files'
    assert calls[1]['name'] == 'write_file'
    assert calls[1]['params']['content'] == 'print("new")'

def test_parse_with_unmatched_tags():
    text = "Just some text with no tags."
    calls = parse_tool_calls(text)
    assert len(calls) == 0

    text = "An incomplete tag <tool_call:read_file"
    calls = parse_tool_calls(text)
    assert len(calls) == 0
