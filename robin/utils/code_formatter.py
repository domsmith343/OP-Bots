import re
from typing import Optional, Tuple, List
import pygments
from pygments.lexers import get_lexer_by_name, guess_lexer
from pygments.formatters import HtmlFormatter
from pygments.util import ClassNotFound

class CodeFormatter:
    # Common language aliases
    LANGUAGE_ALIASES = {
        'js': 'javascript',
        'ts': 'typescript',
        'py': 'python',
        'rb': 'ruby',
        'rs': 'rust',
        'go': 'golang',
        'sh': 'bash',
        'zsh': 'bash',
        'kt': 'kotlin',
        'ktm': 'kotlin',
        'kts': 'kotlin',
        'swift': 'swift',
        'java': 'java',
        'c': 'c',
        'cpp': 'cpp',
        'h': 'cpp',
        'hpp': 'cpp',
        'cs': 'csharp',
        'php': 'php',
        'html': 'html',
        'css': 'css',
        'sql': 'sql',
        'md': 'markdown',
        'json': 'json',
        'xml': 'xml',
        'yaml': 'yaml',
        'yml': 'yaml',
    }

    @staticmethod
    def detect_language(code: str, hint: Optional[str] = None) -> str:
        """Detect the programming language of the code"""
        if hint:
            # Try to use the hint first
            hint = hint.lower()
            if hint in CodeFormatter.LANGUAGE_ALIASES:
                hint = CodeFormatter.LANGUAGE_ALIASES[hint]
            try:
                get_lexer_by_name(hint)
                return hint
            except ClassNotFound:
                pass

        # Try to guess the language
        try:
            lexer = guess_lexer(code)
            return lexer.name.lower()
        except ClassNotFound:
            return 'text'

    @staticmethod
    def extract_code_blocks(text: str) -> List[Tuple[str, str, str]]:
        """Extract code blocks from text with language hints"""
        # Match both ```language and ``` blocks
        pattern = r'```(?:(\w+)\n)?(.*?)```'
        matches = re.finditer(pattern, text, re.DOTALL)
        
        blocks = []
        for match in matches:
            lang_hint = match.group(1) or ''
            code = match.group(2).strip()
            if code:
                blocks.append((code, lang_hint, ''))
        
        return blocks

    @staticmethod
    def format_code(code: str, language: str) -> str:
        """Format code with syntax highlighting"""
        try:
            lexer = get_lexer_by_name(language)
            formatter = HtmlFormatter(style='monokai')
            highlighted = pygments.highlight(code, lexer, formatter)
            return highlighted
        except ClassNotFound:
            return code

    @staticmethod
    def create_code_embed(code: str, language: str, title: str = "Code") -> str:
        """Create a formatted code block for Discord"""
        formatted_code = CodeFormatter.format_code(code, language)
        return f"```{language}\n{formatted_code}\n```"

    @staticmethod
    def format_code_response(response: str) -> str:
        """Format a response containing code blocks"""
        blocks = CodeFormatter.extract_code_blocks(response)
        formatted_response = response

        for code, lang_hint, _ in blocks:
            language = CodeFormatter.detect_language(code, lang_hint)
            formatted_code = CodeFormatter.create_code_embed(code, language)
            # Replace the original code block with the formatted one
            formatted_response = formatted_response.replace(
                f"```{lang_hint}\n{code}\n```" if lang_hint else f"```\n{code}\n```",
                formatted_code
            )

        return formatted_response 