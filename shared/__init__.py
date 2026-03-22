"""
shared - 共享模块
"""
from .mcp_config import MCPConfig, get_project_root, get_mcp_server_path
from .utils import (
    format_diff_summary,
    format_file_tree,
    format_issues_report,
    format_score,
    generate_review_summary,
    severity_icon,
    timestamp,
    json_dumps_safe
)

__all__ = [
    'MCPConfig',
    'get_project_root',
    'get_mcp_server_path',
    'format_diff_summary',
    'format_file_tree',
    'format_issues_report',
    'format_score',
    'generate_review_summary',
    'severity_icon',
    'timestamp',
    'json_dumps_safe'
]
