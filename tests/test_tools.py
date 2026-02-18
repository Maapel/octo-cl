# octo-cl/tests/test_tools.py

import os
from octo_cl.tools import ToolRegistry

def test_read_write_file(tmp_path):
    tr = ToolRegistry(root_dir=str(tmp_path))
    
    # Test write
    write_result = tr.write_file(path="test.txt", content="hello tools")
    assert "Successfully wrote" in write_result
    assert (tmp_path / "test.txt").read_text() == "hello tools"
    
    # Test read
    read_result = tr.read_file(path="test.txt")
    assert read_result == "hello tools"

def test_tool_safety(tmp_path):
    tr = ToolRegistry(root_dir=str(tmp_path))
    
    # Attempt path traversal
    result = tr.read_file(path="../../etc/passwd")
    assert "Error: Access denied" in result
    
    result = tr.write_file(path="/tmp/hack.sh", content="malicious")
    assert "Error: Access denied" in result

def test_list_files(tmp_path):
    tr = ToolRegistry(root_dir=str(tmp_path))
    (tmp_path / "a.py").touch()
    (tmp_path / "b.txt").touch()
    
    result = tr.list_files(path=".")
    assert "a.py" in result
    assert "b.txt" in result
