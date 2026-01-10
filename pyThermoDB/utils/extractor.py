# import libs
import logging
import yaml
import re
from typing import Optional, List, Dict, Any, Tuple
from pythermodb_settings.utils import measure_time
# local

# NOTE: logger
logger = logging.getLogger(__name__)


class YAMLExtractor:
    """Extract and validate YAML content from mixed-format strings."""

    def extract_yaml_sections(self, text: str) -> List[Dict[str, Any]]:
        """
        Extract all valid YAML sections from a mixed-format string.

        Args:
            text: String potentially containing YAML content

        Returns:
            List of dictionaries containing extracted YAML data and metadata
        """
        results = []

        # Method 1: Try to find explicit YAML document markers
        yaml_docs = self._extract_by_markers(text)

        # Method 2: Extract multiple YAML blocks throughout the text
        yaml_blocks = self._extract_multiple_yaml_blocks(text)

        # Combine results, avoiding duplicates
        all_results = yaml_docs + yaml_blocks

        # Remove duplicates based on content
        seen_content = []
        for result in all_results:
            content_str = str(result['content'])
            if content_str not in seen_content:
                results.append(result)
                seen_content.append(content_str)

        return results

    def _extract_by_markers(self, text: str) -> List[Dict[str, Any]]:
        """Extract YAML content between document markers (--- and ...)."""
        results = []

        # Pattern to find YAML documents with explicit markers
        # Look for --- at start of line
        pattern = r'^---\s*$(.+?)(?:^\.\.\.\s*$|\Z)'
        matches = re.findall(pattern, text, re.MULTILINE | re.DOTALL)

        for match in matches:
            parsed = self._safe_yaml_parse(match)
            if parsed is not None and not self._is_simple_string(parsed, match):
                results.append({
                    'content': parsed,
                    'raw': f"---\n{match.strip()}\n...",
                    'method': 'markers',
                    'valid': True,
                    'start_pos': text.find(f"---\n{match.strip()}")
                })

        # Also try without end marker
        pattern2 = r'^---\s*\n(.+?)(?=^---|\Z)'
        matches2 = re.findall(pattern2, text, re.MULTILINE | re.DOTALL)

        for match in matches2:
            if match not in [m for m in matches]:  # Avoid duplicates
                parsed = self._safe_yaml_parse(match)
                if parsed is not None and not self._is_simple_string(parsed, match):
                    results.append({
                        'content': parsed,
                        'raw': f"---\n{match.strip()}",
                        'method': 'markers',
                        'valid': True,
                        'start_pos': text.find(f"---\n{match.strip()}")
                    })

        return results

    def _extract_multiple_yaml_blocks(self, text: str) -> List[Dict[str, Any]]:
        """Extract multiple YAML blocks from text, even if separated by non-YAML content."""
        results = []
        lines = text.split('\n')
        current_block = []
        yaml_started = False
        indent_stack = []
        block_start_idx = 0
        consecutive_non_yaml = 0
        max_non_yaml_lines = 2  # Allow up to 2 non-YAML lines before considering block ended

        for i, line in enumerate(lines):
            stripped = line.strip()

            if not yaml_started:
                # Looking for start of a YAML block
                if self._looks_like_yaml_start(line, lines, i):
                    # Skip if this is inside a marker block already processed
                    if stripped == '---':
                        # This might be a marker block, skip it
                        continue

                    yaml_started = True
                    current_block = [line]
                    block_start_idx = i
                    consecutive_non_yaml = 0
                    if stripped and not stripped.startswith('#'):
                        indent_stack = [len(line) - len(line.lstrip())]
            else:
                # We're in a potential YAML block
                if not stripped:
                    # Empty line - might be part of YAML
                    current_block.append(line)
                    consecutive_non_yaml = 0
                elif stripped.startswith('#'):
                    # Comment - part of YAML
                    current_block.append(line)
                    consecutive_non_yaml = 0
                elif self._is_yaml_continuation(line, indent_stack):
                    # Definitely YAML continuation
                    current_block.append(line)
                    consecutive_non_yaml = 0

                    # Update indent stack
                    if not line.strip().startswith('#'):
                        current_indent = len(line) - len(line.lstrip())
                        if indent_stack and current_indent < indent_stack[-1]:
                            # Dedent - pop from stack
                            while indent_stack and indent_stack[-1] > current_indent:
                                indent_stack.pop()
                        elif current_indent > 0 and (not indent_stack or current_indent > indent_stack[-1]):
                            # New indent level
                            indent_stack.append(current_indent)
                else:
                    # This might not be YAML
                    # Try parsing what we have so far
                    yaml_text = '\n'.join(current_block).rstrip()
                    parsed = self._safe_yaml_parse(yaml_text)

                    if parsed is not None and not self._is_simple_string(parsed, yaml_text):
                        # We have valid YAML, but current line doesn't continue it
                        # Check if we should save this block
                        if len(current_block) > 1 or self._is_structured_yaml(parsed):
                            results.append({
                                'content': parsed,
                                'raw': yaml_text,
                                'method': 'block_extraction',
                                'valid': True,
                                'start_line': block_start_idx,
                                'end_line': i - 1
                            })

                        # Reset for next potential block
                        yaml_started = False
                        current_block = []
                        indent_stack = []
                        consecutive_non_yaml = 0

                        # Check if current line starts a new YAML block
                        if self._looks_like_yaml_start(line, lines, i):
                            yaml_started = True
                            current_block = [line]
                            block_start_idx = i
                            if stripped and not stripped.startswith('#'):
                                indent_stack = [len(line) - len(line.lstrip())]
                    else:
                        # Not valid YAML yet, maybe this line is part of it
                        # But if we see too many non-YAML lines, stop
                        if self._definitely_not_yaml(line):
                            consecutive_non_yaml += 1
                            if consecutive_non_yaml > max_non_yaml_lines:
                                # Too many non-YAML lines, end this block attempt
                                yaml_started = False
                                current_block = []
                                indent_stack = []
                                consecutive_non_yaml = 0
                            else:
                                current_block.append(line)
                        else:
                            current_block.append(line)
                            consecutive_non_yaml = 0

        # Check last block
        if yaml_started and current_block:
            yaml_text = '\n'.join(current_block).rstrip()
            parsed = self._safe_yaml_parse(yaml_text)
            if parsed is not None and not self._is_simple_string(parsed, yaml_text):
                if len(current_block) > 1 or self._is_structured_yaml(parsed):
                    results.append({
                        'content': parsed,
                        'raw': yaml_text,
                        'method': 'block_extraction',
                        'valid': True,
                        'start_line': block_start_idx,
                        'end_line': len(lines) - 1
                    })

        return results

    def _looks_like_yaml_start(
            self,
            line: str,
            lines: Optional[List[str]] = None,
            line_idx: int = -1
    ) -> bool:
        """Check if a line looks like it could start a YAML document."""
        stripped = line.strip()

        if not stripped:
            return False

        # YAML document markers
        if stripped in ['---', '...']:
            return True

        # DON'T treat standalone comments as YAML start
        if stripped.startswith('#'):
            return False

        # Key-value pair check with better validation
        if self._looks_like_yaml_key_value(stripped, line, lines, line_idx):
            return True

        # List item
        if re.match(r'^-\s+', stripped):
            return True

        return False

    def _looks_like_yaml_key_value(
            self,
            stripped: str,
            full_line: str,
            lines: Optional[List[str]] = None,
            line_idx: int = -1
    ) -> bool:
        """Enhanced key-value pair detection with context awareness."""
        # Basic key-value pattern
        key_value_match = re.match(
            r'^([a-zA-Z_][\w\-]*)\s*:\s*(.*?)$', stripped)
        if not key_value_match:
            return False

        key, value = key_value_match.groups()

        # Skip URLs and times
        if re.match(r'^\d+:\d+', stripped) or '://' in stripped:
            return False

        # Check if this appears to be in a comment context
        if lines and line_idx >= 0:
            # Look at the original line in context to see if it's part of a comment
            if self._appears_in_comment_context(lines, line_idx, key):
                return False

        # Additional validation for key-value pairs

        # 1. Very short keys with no meaningful value are suspicious
        if len(key) <= 2 and not value.strip():
            return False

        # 2. Single letter keys are often not real YAML keys
        if len(key) == 1:
            return False

        # 3. If we have context, check if next lines make sense
        if lines and line_idx >= 0:
            if not self._has_reasonable_yaml_continuation(lines, line_idx):
                return False

        return True

    def _appears_in_comment_context(self, lines: List[str], line_idx: int, key: str) -> bool:
        """Check if a key appears to be part of a comment rather than real YAML."""
        current_line = lines[line_idx]

        # Check if the line starts with # (even before the key)
        # This handles cases like "# Some text OK: value"
        hash_pos = current_line.find('#')
        key_pos = current_line.find(key + ':')

        if hash_pos >= 0 and key_pos >= 0 and hash_pos < key_pos:
            # The key appears after a # comment marker
            return True

        # Check if previous lines suggest we're in a comment block
        comment_context = 0
        for i in range(max(0, line_idx - 3), line_idx):
            if i < len(lines) and lines[i].strip().startswith('#'):
                comment_context += 1

        # If surrounded by comments and key is short, it's likely part of comment
        if comment_context >= 2 and len(key) <= 3:
            return True

        return False

    def _has_reasonable_yaml_continuation(self, lines: List[str], line_idx: int) -> bool:
        """Check if the lines following a potential YAML key make sense."""
        if line_idx + 1 >= len(lines):
            return True  # End of file, can't check continuation

        # Look at next 3 lines
        next_few_lines = lines[line_idx + 1:line_idx + 4]

        yaml_like_continuations = 0
        non_yaml_continuations = 0

        for next_line in next_few_lines:
            stripped = next_line.strip()
            if not stripped:
                continue  # Skip empty lines

            # Check if it looks like YAML continuation
            if (stripped.startswith('  ') or  # Indented (likely YAML)
                re.match(r'^[a-zA-Z_][\w\-]*\s*:', stripped) or  # Another key
                stripped.startswith('- ') or  # List item
                    stripped.startswith('#')):  # Comment
                yaml_like_continuations += 1
            else:
                non_yaml_continuations += 1

        # If we see more non-YAML than YAML continuations, it's probably not YAML
        return yaml_like_continuations >= non_yaml_continuations

    def _is_yaml_continuation(self, line: str, indent_stack: List[int]) -> bool:
        """Check if a line continues YAML structure based on indentation and content."""
        stripped = line.strip()

        # Empty lines are continuations
        if not stripped:
            return True

        # Comments are continuations ONLY if we're already in a YAML block
        if stripped.startswith('#'):
            return True

        # Check for YAML patterns
        # Key-value pair (with better validation)
        if self._looks_like_yaml_key_value(stripped, line):
            return True

        # List item
        if stripped.startswith('- '):
            return True

        # Multi-line string indicators
        if stripped in ['|', '>', '|-', '>-', '|+', '>+']:
            return True

        # Check indentation for multi-line values
        if indent_stack:
            current_indent = len(line) - len(line.lstrip())
            # If indented at least as much as something in the stack
            if current_indent > 0 and current_indent >= min(indent_stack):
                return True

        # Check for continuation of list items or values (indented content)
        if re.match(r'^\s+\S', line):
            return True

        # Check for quoted strings that might span lines
        if stripped.startswith('"') or stripped.startswith("'"):
            return True

        return False

    def _definitely_not_yaml(self, line: str) -> bool:
        """Check if a line is definitely not YAML."""
        stripped = line.strip()

        if not stripped:
            return False  # Empty lines could be part of YAML

        # Standalone comments at the beginning are not YAML content
        if stripped.startswith('#'):
            return True

        # Check for patterns that are definitely not YAML
        # Sentences without YAML structure
        if len(stripped) > 20 and ':' not in stripped and not stripped.startswith('- '):
            # Looks like prose
            if ' ' in stripped and not stripped.startswith('#'):
                words = stripped.split()
                if len(words) > 3:
                    # Multiple words without YAML structure
                    return True

        return False

    def _is_simple_string(self, parsed: Any, original: str) -> bool:
        """Check if parsed result is just a simple string without structure."""
        if not isinstance(parsed, str):
            return False

        # If original has YAML structure indicators but parsed as simple string
        if any(indicator in original for indicator in [':', '- ', '{', '[', '\n']):
            return False

        return True

    def _is_structured_yaml(self, parsed: Any) -> bool:
        """Check if parsed YAML has structure (not just a scalar)."""
        if isinstance(parsed, (dict, list)):
            return True
        if isinstance(parsed, str) and '\n' in parsed:
            return True  # Multi-line string
        return False

    def _safe_yaml_parse(self, text: str) -> Optional[Any]:
        """Safely parse YAML content."""
        if not text or not text.strip():
            return None

        try:
            # Try to load as YAML
            result = yaml.safe_load(text)
            return result
        except yaml.YAMLError:
            # Try with safe_load_all for multiple documents
            try:
                documents = list(yaml.safe_load_all(text))
                if len(documents) == 1:
                    return documents[0]
                elif len(documents) > 1:
                    return documents
            except yaml.YAMLError:
                pass

        return None

    def validate_yaml(self, text: str) -> Tuple[bool, Optional[str]]:
        """
        Validate if a string is valid YAML.

        Args:
            text: String to validate

        Returns:
            Tuple of (is_valid, error_message)
        """
        try:
            yaml.safe_load(text)
            return True, None
        except yaml.YAMLError as e:
            return False, str(e)

    @measure_time
    def extract_and_validate(
        self,
        text: str,
        **kwargs,
    ) -> Dict[str, Any]:
        """
        Extract YAML sections and provide validation results.

        Args:
            text: String potentially containing YAML
            kwargs: mode, Literal['silent', 'log', 'attach'], optional

        Returns:
            Dictionary with extraction results and validation status
        """
        sections = self.extract_yaml_sections(text)

        return {
            'found_yaml': len(sections) > 0,
            'num_sections': len(sections),
            'sections': sections,
            'summary': self._generate_summary(sections)
        }

    def _generate_summary(self, sections: List[Dict[str, Any]]) -> str:
        """Generate a summary of extracted YAML sections."""
        if not sections:
            return "No valid YAML sections found"

        summary = f"Found {len(sections)} YAML section(s):\n"
        for i, section in enumerate(sections, 1):
            content_type = type(section['content']).__name__
            method = section['method']

            # Show brief content preview
            if isinstance(section['content'], dict):
                keys = list(section['content'].keys())[:3]
                preview = f"Keys: {', '.join(keys)}"
                if len(section['content']) > 3:
                    preview += f"... ({len(section['content'])} total)"
            elif isinstance(section['content'], list):
                preview = f"List with {len(section['content'])} items"
            else:
                preview = str(section['content'])[:50]
                if len(str(section['content'])) > 50:
                    preview += "..."

            summary += f"  {i}. Type: {content_type}, Method: {method}\n"
            summary += f"     Preview: {preview}\n"

            # Add line information if available
            if 'start_line' in section:
                summary += f"     Location: Lines {section['start_line']}-{section['end_line']}\n"

        return summary
