# octo-cl/tests/test_context_builder.py

import os
from octo_cl.context_builder import ContextBuilder

def test_get_directory_tree(tmp_path):
    # Create a dummy project structure
    d = tmp_path / "project"
    d.mkdir()
    (d / "file1.py").write_text("print('hello')")
    (d / "subdir").mkdir()
    (d / "subdir" / "file2.txt").write_text("content")
    (d / ".git").mkdir()
    (d / ".git" / "config").write_text("git stuff")
    
    cb = ContextBuilder(root_dir=str(d))
    tree = cb.get_directory_tree()
    
    assert "file1.py" in tree
    assert "subdir/" in tree
    assert "file2.txt" in tree
    assert ".git/" not in tree # Should be ignored by default

def test_get_file_content(tmp_path):
    d = tmp_path / "project"
    d.mkdir()
    f = d / "test.py"
    f.write_text("hello world")
    
    cb = ContextBuilder(root_dir=str(d))
    content = cb.get_file_content("test.py")
    
    assert "--- FILE: test.py ---" in content
    assert "hello world" in content

def test_get_file_content_safety(tmp_path):
    d = tmp_path / "project"
    d.mkdir()
    
    cb = ContextBuilder(root_dir=str(d))
    # Try to access something outside the root
    content = cb.get_file_content("../outside.txt")
    
    assert "Error: Access denied" in content
