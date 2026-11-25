# AI Agent Engineering Curriculum

A developer-focused, source-controlled course on building secure, reliable, and auditable AI agents. The course distinguishes model inference, agent framework primitives, agent harness runtime governance, MCP capability exchange, and enterprise application authorization.

## Start here

- [Engineering Software with AI Coding Agents](technical-documents/engineering-software-with-ai-coding-agents/README.md) — Codex and Claude Code across the SDLC, harness extensions, verification, isolation, security, and enterprise governance.

- [AI Agent Workflow and Orchestration Patterns](technical-documents/ai-agent-workflow-orchestration-patterns-guide.tex) — comprehensive architecture comparison of sequential chains, parallel workers, routers, ReAct loops, planners, supervisors, peer agents, evaluators and approval gates; includes twelve editable TikZ diagrams, Python examples, security and testing criteria.

- [Agent Skills Engineering: Specification, Architecture, Testing, and Security](technical-documents/agent-skills-engineering-guide.tex) — detailed technical guide covering skill packages, cross-agent integration, lifecycle validation, testing, and secure deployment.

- [Multi-Language AI Agent Skills: Verified Repositories, Installation and Governance](technical-documents/agent-skills-multilanguage-guide.tex) — research guide comparing installable skills with registries and pattern references, with verified CLI syntax, language-specific choices, templates, and a skill security audit process.
- [Agent Engineering Standards: SKILL.md, AGENTS.md, MCP, and Agent Harnesses](technical-documents/agent-engineering-standards-skills-agents-mcp-harnesses.tex) — integrated technical reference with architecture diagrams, implementation patterns, MCP versioning, security controls, and validation guidance.
- [L01-L16 Beamer laboratory presentations](curriculum/lab-presentations/README.md) -- instructional slide decks aligned to each week.


- [Comprehensive 16-week syllabus](curriculum/ai-agent-engineering-comprehensive-syllabus.tex) — 12 technical modules, 16 engineering labs, approximately 160 hours, midterm, and final architecture review.
- [AI Agent Harness Architecture and Engineering Guide](technical-documents/ai-agent-harness-architecture-and-engineering-guide.tex) — standalone technical reference covering the control loop, tools, context compaction, state, verification, guardrails, orchestration, implementation phases, and a coding-agent lab.
- [AGENTS.md: Repository-Aware Guidance for AI Coding Agents](technical-documents/agents-md-repository-guidance.tex) — technical guide to repository-scoped agent instructions, tool compatibility, instruction layering, validation, and a ready-to-adapt AGENTS.md template for `latex-docs`.
- [Curriculum collection](curriculum/README.md) — build instructions and source provenance.

- [OpenAI Codex Custom Subagents: Configuration, Precedence, and Secure Orchestration](technical-documents/codex-custom-subagents-technical-guide.tex) — subagent TOML definitions, scope and precedence, model overrides, secure delegation, and verification.
- [OpenAI Codex Integration with GitHub Copilot](technical-documents/codex-github-copilot-integration-guide.tex) — GitHub-hosted issue delegation, VS Code local/cloud operation, authentication, permissions, enterprise policy, AGENTS.md, CI/CD, troubleshooting and measurable rollout acceptance criteria.

## Scope and safeguards

The learning sequence moves from a framework-free Python agent to LangGraph/framework selection, custom harness controls, MCP integration, context management, policy enforcement, multi-agent orchestration, evaluation, observability, and deployment.

The capstone is a **read-only GitHub CodeQL investigation agent**: alert retrieval, evidence-backed findings, policy evaluation, and approval recommendations. Discovering a tool does not grant authorization; alert dismissals, protected-branch bypasses, and other state-changing actions require separately validated permissions and approval.

Training materials propose design and test exercises, **not** evidence of an operationally deployed or certified enterprise security control. Verify course links, software versions, and the deployed MCP protocol revision before implementation.

## Build

From the repository root:

```bash
make preflight
make build-category-data-systems
```

To build just the source with pdfLaTeX:

```bash
cd src/data-systems/ai-agent-engineering/curriculum
latexmk -pdf -interaction=nonstopmode -halt-on-error -file-line-error ai-agent-engineering-comprehensive-syllabus.tex
```

The syllabus is a self-contained LaTeX source with its prerequisite figure typeset natively. No external graphic assets or paid API keys are required to compile it.

## Provenance

Curriculum edition 1.0, source review dated November 12, 2026. The program was developed from *Agent Harness, Agent Framework, and MCP: Which Layer Owns What?*, plus published learning resources. Sections on timing, grading, labs, and capstone requirements are instructional design proposals, not quoted standards.

## Related domains

- [Data Systems](../README.md)
- [Architecture](../../architecture/README.md)
- [Application Security](../../security/README.md)
- [DevOps](../../devops/README.md)

## Application Security specialization

- [Agent Harness Engineering for Application Security](../../security/application-security/agent-harness-engineering/README.md) — cross-domain reference architecture, AppSec workflow controls, Python example, PlantUML views, threat model and progressive implementation labs.
