# Computer Security Engineering and Information Assurance Documentation Suite

**Primary study source:** Matt Bishop, *Computer Security: Art and Science*, **2nd ed. (2019)**, ISBN 978-0-321-71233-2. This is a **newly authored study companion**, not a reprint, derivative transcription of textbook exercises, publisher-endorsed course, standard, security attestation, or authorization to test real systems.

**Delivery status:** original source material and synthetic example code. Published LaTeX roots require verification through repository build CI; local code tests and any resulting run reports must be evaluated separately.

## Scope and provenance

- **BOOK ALIGNED:** 31 chapter headings, high-level study areas, conceptual models, and reading prompts anchored to Bishop's chapter sequence. Full technical treatment remains in the lawfully accessed book; this public repository contains no source PDF or copied figure.
- **INDEPENDENT ENGINEERING:** curriculum prerequisites, scenarios, formal-policy comparisons, Python/C/C++ programs, validation procedures, workflows, risk/evidence records, and local acceptance gates.
- **EXTERNAL SOURCES:** authoritative, dated NIST, OWASP, MITRE ATT&CK and ISO/IEC material is referenced for contemporary applicability. Candidate mappings are thematic unless a versioned exact reference has been independently verified.

## Read and build

```bash
make preflight
make build-category-security
python3 -m unittest discover -s src/security/computer-security-art-and-science/examples/python -p 'test_*.py'
cc -std=c99 -Wall -Wextra -Wpedantic -Werror src/security/computer-security-art-and-science/examples/c/checked_copy.c -o /tmp/ces-copy && /tmp/ces-copy
c++ -std=c++17 -Wall -Wextra -Wpedantic -Werror src/security/computer-security-art-and-science/examples/cpp/object_authorization.cpp -o /tmp/ces-auth && /tmp/ces-auth
```

The existing LaTeX CI performs changed-root compilation. The new [lab workflow](../../../../.github/workflows/bishop-security-labs.yml) runs read-only, no-network-target example tests; it does not provision infrastructure, enable GHAS, or certify security.

## 31 textbook-aligned study guides

| Chapter | Book chapter | Independent guide |
|---|---|---|
| 01 | An Overview of Computer Security | [Guide](study-guides/chapter-01-an-overview-of-computer-security.tex) |
| 02 | Access Control Matrix | [Guide](study-guides/chapter-02-access-control-matrix.tex) |
| 03 | Foundational Results | [Guide](study-guides/chapter-03-foundational-results.tex) |
| 04 | Security Policies | [Guide](study-guides/chapter-04-security-policies.tex) |
| 05 | Confidentiality Policies | [Guide](study-guides/chapter-05-confidentiality-policies.tex) |
| 06 | Integrity Policies | [Guide](study-guides/chapter-06-integrity-policies.tex) |
| 07 | Availability Policies | [Guide](study-guides/chapter-07-availability-policies.tex) |
| 08 | Hybrid Policies | [Guide](study-guides/chapter-08-hybrid-policies.tex) |
| 09 | Noninterference and Policy Composition | [Guide](study-guides/chapter-09-noninterference-and-policy-composition.tex) |
| 10 | Basic Cryptography | [Guide](study-guides/chapter-10-basic-cryptography.tex) |
| 11 | Key Management | [Guide](study-guides/chapter-11-key-management.tex) |
| 12 | Cipher Techniques | [Guide](study-guides/chapter-12-cipher-techniques.tex) |
| 13 | Authentication | [Guide](study-guides/chapter-13-authentication.tex) |
| 14 | Design Principles | [Guide](study-guides/chapter-14-design-principles.tex) |
| 15 | Representing Identity | [Guide](study-guides/chapter-15-representing-identity.tex) |
| 16 | Access Control Mechanisms | [Guide](study-guides/chapter-16-access-control-mechanisms.tex) |
| 17 | Information Flow | [Guide](study-guides/chapter-17-information-flow.tex) |
| 18 | Confinement Problem | [Guide](study-guides/chapter-18-confinement-problem.tex) |
| 19 | Introduction to Assurance | [Guide](study-guides/chapter-19-introduction-to-assurance.tex) |
| 20 | Building Systems with Assurance | [Guide](study-guides/chapter-20-building-systems-with-assurance.tex) |
| 21 | Formal Methods | [Guide](study-guides/chapter-21-formal-methods.tex) |
| 22 | Evaluating Systems | [Guide](study-guides/chapter-22-evaluating-systems.tex) |
| 23 | Malware | [Guide](study-guides/chapter-23-malware.tex) |
| 24 | Vulnerability Analysis | [Guide](study-guides/chapter-24-vulnerability-analysis.tex) |
| 25 | Auditing | [Guide](study-guides/chapter-25-auditing.tex) |
| 26 | Intrusion Detection | [Guide](study-guides/chapter-26-intrusion-detection.tex) |
| 27 | Attacks and Responses | [Guide](study-guides/chapter-27-attacks-and-responses.tex) |
| 28 | Network Security | [Guide](study-guides/chapter-28-network-security.tex) |
| 29 | System Security | [Guide](study-guides/chapter-29-system-security.tex) |
| 30 | User Security | [Guide](study-guides/chapter-30-user-security.tex) |
| 31 | Program Security | [Guide](study-guides/chapter-31-program-security.tex) |

## Curriculum, models and standards

- [36-week prerequisite curriculum](curriculum/prerequisite-based-curriculum.tex)
- [Formal protection, information-flow and assurance reference](reference/formal-protection-information-flow-and-assurance.tex)
- [Standards provenance, status and applicability](reference/standards-provenance-and-applicability.tex)
- [Candidate control mapping and evidence standard](controls/control-mapping-and-evidence.tex) and [machine-readable mapping](controls/control-crosswalk.csv)

## Original laboratories

| Lab | Topic | Specification |
|---|---|---|
| 01 | Finite Access Matrix and Unauthorized Grant | [LaTeX](labs/lab-01-finite-access-matrix-and-unauthorized-grant.tex) |
| 02 | Two-Run Noninterference Counterexample | [LaTeX](labs/lab-02-two-run-noninterference-counterexample.tex) |
| 03 | Length-Checked Buffer Boundary | [LaTeX](labs/lab-03-length-checked-buffer-boundary.tex) |
| 04 | Object-Level Authorization in C++ | [LaTeX](labs/lab-04-object-level-authorization-in-c.tex) |
| 05 | Trust Boundary Threat Model | [LaTeX](labs/lab-05-trust-boundary-threat-model.tex) |
| 06 | Vulnerability Validation and Remediation | [LaTeX](labs/lab-06-vulnerability-validation-and-remediation.tex) |
| 07 | Least-Privilege GitHub Actions Security Gate | [LaTeX](labs/lab-07-least-privilege-github-actions-security-gate.tex) |
| 08 | Assurance Case and Final Evaluation | [LaTeX](labs/lab-08-assurance-case-and-final-evaluation.tex) |

[Executable example programs](examples/README.md) and [read-only CI integration reference](ci-cd/security-laboratories-github-actions.tex).

## Procedures and assessments

- [Threat modeling](procedures/threat-modeling-procedure.tex)
- [Vulnerability assessment and remediation](procedures/vulnerability-assessment-procedure.tex)
- [Secure coding and review](procedures/secure-coding-and-review.tex)
- [Assurance and compliance assessment](assessment/assurance-and-compliance-assessment.tex)

## Independently maintained Template–Blank pairs

Every row links to two separate, standalone LaTeX roots. Templates contain reviewer guidance; Blanks contain empty printable fields and no example responses. Neither implies execution, conformance or approval.

| Form | Guided Template | Print Blank |
|---|---|---|
| Threat Model and Abuse-Case Register | [Template](forms/threat-model-template.tex) | [Blank](forms/threat-model-blank.tex) |
| Access Policy and Authorization Decision Matrix | [Template](forms/access-control-template.tex) | [Blank](forms/access-control-blank.tex) |
| Formal Security Claim and Proof Obligation | [Template](forms/formal-proof-template.tex) | [Blank](forms/formal-proof-blank.tex) |
| Detection Engineering and ATTACK Mapping | [Template](forms/threat-detection-template.tex) | [Blank](forms/threat-detection-blank.tex) |
| Vulnerability Assessment and Remediation Record | [Template](forms/vulnerability-assessment-template.tex) | [Blank](forms/vulnerability-assessment-blank.tex) |
| Security Control and Evidence Traceability | [Template](forms/control-traceability-template.tex) | [Blank](forms/control-traceability-blank.tex) |
| Security Deviation and Risk Acceptance | [Template](forms/deviation-template.tex) | [Blank](forms/deviation-blank.tex) |
| Secure Design and Code Review Record | [Template](forms/secure-review-template.tex) | [Blank](forms/secure-review-blank.tex) |
| DevSecOps CI Gate and Supply-Chain Record | [Template](forms/ci-gate-template.tex) | [Blank](forms/ci-gate-blank.tex) |
| Assurance Case and Compliance Assessment | [Template](forms/assurance-case-template.tex) | [Blank](forms/assurance-case-blank.tex) |

## Reuse and avoid duplication

| Canonical existing collection | Use here |
|---|---|
| [Security engineering volumes](../security-engineering/README.md) | Broad enterprise security, threat modeling, crypto, DFIR |
| [SAST engineering suite](../application-security/sast/README.md) | Tool-specific SAST labs, assessment and CI patterns |
| [Application assessment](../application-security/assessment/README.md) | Secure code assessment methods |
| [GHAS](../github-advanced-security/) | Code scanning, secret scanning, dependency response |
| [Security standards](../standards/) | Existing ISO/OWASP/CIS references |
| [DevOps](../../devops/README.md) | Build and delivery engineering |
| [Programming language standards](../../programming/languages/README.md) | C/C++ and Python style/security guidance |

Do not turn a thematic standards crosswalk into an invented normative control equivalence. Actual audits require system-specific applicability, authoritative standard texts, evidence and independent review. The repo is public: no confidential assets or real incident material.
