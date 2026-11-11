# Repository agent guidance

<!-- codebase-memory-mcp:start -->
## Codebase Memory

For structural codebase exploration, use the installed `codebase-memory` skill
and its MCP graph tools before file-by-file search.

1. Confirm the repository graph and freshness with `list_projects` or
   `index_status`.
2. Prefer `search_graph`, `trace_path`, and `get_code_snippet` for symbols and
   relationships.
3. Run `check_index_coverage` for every material path used as evidence.
4. Use source search for configuration, string literals, and every reported
   coverage gap.

Treat graph results as best-effort evidence. A clean coverage result does not
prove completeness.
<!-- codebase-memory-mcp:end -->
