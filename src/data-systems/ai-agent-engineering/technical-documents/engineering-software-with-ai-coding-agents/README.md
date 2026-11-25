# Engineering Software with AI Coding Agents

[Technical reference (LaTeX)](engineering-software-with-ai-coding-agents.tex) — Codex, Claude Code, agent harnesses and autonomous software development workflows. Includes 30 chapters, 24 editable TikZ views, 18 patterns, 15 labs, and eight case studies.

- [Chapter sources](chapters/README.md)
- [Diagram sources](diagrams/README.md)
- [Reference implementation and skills](examples/README.md)
- [Governance artifacts](governance/README.md)
- [Source register](source-register.csv)
- [Validation evidence and limitations](validation/README.md)

Build with the repository-supported pdfLaTeX/latexmk toolchain and shell escape for minted. From this directory, `latexmk -pdf -shell-escape -interaction=nonstopmode -halt-on-error -file-line-error engineering-software-with-ai-coding-agents.tex`; for the repository house style set `TEXINPUTS` to include its `tooling/latex//` and `tooling/styles/latex//`. The original offline prototype is not a security sandbox. Native CLI/MCP execution and enterprise controls are not qualified. PDF and build logs are generated, not canonical sources.
