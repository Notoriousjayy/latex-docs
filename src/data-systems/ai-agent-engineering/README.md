# AI Agent Engineering Curriculum

A developer-focused, source-controlled course on building secure, reliable, and auditable AI agents. The course distinguishes model inference, agent framework primitives, agent harness runtime governance, MCP capability exchange, and enterprise application authorization.

## Start here

- [Comprehensive 16-week syllabus](curriculum/ai-agent-engineering-comprehensive-syllabus.tex) — 12 technical modules, 16 engineering labs, approximately 160 hours, midterm, and final architecture review.
- [Curriculum collection](curriculum/README.md) — build instructions and source provenance.

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
