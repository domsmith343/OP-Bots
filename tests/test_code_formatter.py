import pytest
from robin.utils.code_formatter import CodeFormatter

def test_detect_language_with_hint():
    """Test language detection with hint"""
    code = "print('Hello, World!')"
    assert CodeFormatter.detect_language(code, "python") == "python"
    assert CodeFormatter.detect_language(code, "py") == "python"

def test_detect_language_without_hint():
    """Test language detection without hint"""
    python_code = "def hello():\n    print('Hello, World!')"
    js_code = "function hello() {\n    console.log('Hello, World!');\n}"
    
    assert CodeFormatter.detect_language(python_code) == "python"
    assert CodeFormatter.detect_language(js_code) == "javascript"

def test_extract_code_blocks():
    """Test code block extraction"""
    text = """
    Here's some Python code:
    ```python
    def hello():
        print('Hello, World!')
    ```
    And some JavaScript:
    ```javascript
    function hello() {
        console.log('Hello, World!');
    }
    ```
    """
    blocks = CodeFormatter.extract_code_blocks(text)
    assert len(blocks) == 2
    assert blocks[0][1] == "python"  # language hint
    assert "def hello()" in blocks[0][0]  # code content
    assert blocks[1][1] == "javascript"
    assert "function hello()" in blocks[1][0]

def test_format_code():
    """Test code formatting"""
    code = "def hello():\n    print('Hello, World!')"
    formatted = CodeFormatter.format_code(code, "python")
    assert "def" in formatted
    assert "print" in formatted

def test_create_code_embed():
    """Test code embed creation"""
    code = "def hello():\n    print('Hello, World!')"
    embed = CodeFormatter.create_code_embed(code, "python")
    assert "```python" in embed
    assert "def hello()" in embed
    assert "```" in embed

def test_format_code_response():
    """Test formatting response with code blocks"""
    response = """
    Here's a Python function:
    ```python
    def hello():
        print('Hello, World!')
    ```
    And a JavaScript function:
    ```javascript
    function hello() {
        console.log('Hello, World!');
    }
    ```
    """
    formatted = CodeFormatter.format_code_response(response)
    assert "```python" in formatted
    assert "```javascript" in formatted
    assert "def hello()" in formatted
    assert "function hello()" in formatted

def test_language_aliases():
    """Test language aliases"""
    assert CodeFormatter.LANGUAGE_ALIASES['js'] == 'javascript'
    assert CodeFormatter.LANGUAGE_ALIASES['py'] == 'python'
    assert CodeFormatter.LANGUAGE_ALIASES['ts'] == 'typescript'

def test_invalid_language():
    """Test handling of invalid language"""
    code = "print('Hello, World!')"
    formatted = CodeFormatter.format_code(code, "invalid_language")
    assert formatted == code  # Should return original code for invalid language

def test_empty_code_block():
    """Test handling of empty code blocks"""
    text = "```\n```"
    blocks = CodeFormatter.extract_code_blocks(text)
    assert len(blocks) == 0  # Should not extract empty blocks

def test_nested_code_blocks():
    """Test handling of nested code blocks"""
    text = """
    ```python
    def example():
        print('''
        ```python
        nested code
        ```
        ''')
    ```
    """
    blocks = CodeFormatter.extract_code_blocks(text)
    assert len(blocks) == 1  # Should only extract the outer block 