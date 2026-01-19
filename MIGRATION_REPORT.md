# LaTeX Docs Repository Migration Report

## Migration Summary

This repository has been reorganized for better maintainability and discoverability.

## New Structure

```text
src/
├── security/
│   ├── appsec/           # Application security programs, guides, user stories
│   ├── certifications/   # CISO, CISSP, CISH study materials
│   ├── cloud-security/   # Cloud security guides and user stories
│   ├── ghas/             # GitHub Advanced Security (CodeQL, Dependabot, Secret Scanning)
│   └── owasp             # OWASP Top 10 and API Security
│
├── architecture/
│   ├── documenting-software-architecture/
│   ├── enterprise/
│   ├── systems-engineering/
│   ├── system-design/
│   └── togaf/
│
├── devops/
│   ├── ci-cd/
│   ├── github/
│   ├── github-actions/
│   ├── gitops/
│   ├── hashicorp-vault/
│   ├── kubernetes/
│   └── nginx/
│
├── data-systems/
│   ├── kafka/
│   └── llm/
│
├── electronics/
├── game-development/
├── mathematics/
├── programming/
├── cloud/
├── ai-ml/
├── media/
├── physics-simulation/
└── personal/
```

## Building PDFs

```bash
make all
# or
./tooling/scripts/build_all.sh
```


## Files by Category

### ai-ml

- `ai-ml/prompt-engineering/prompt-engineering-curriculum.tex`
- `ai-ml/prompt-engineering/prompt-engineering-roadmap.tex`

### architecture

- `architecture/documenting-software-architecture/architecture-documentation-beyond-views.tex`
- `architecture/documenting-software-architecture/architecture-documentation-review-across-project-phases.tex`
- `architecture/documenting-software-architecture/architecture-documentation-template.tex`
- `architecture/documenting-software-architecture/architecture-framework-mapping.tex`
- `architecture/documenting-software-architecture/architecture-overview-presentation.tex`
- `architecture/documenting-software-architecture/architecture-playbook.tex`
- `architecture/documenting-software-architecture/aspects-style.tex`
- `architecture/documenting-software-architecture/builder-viewpoint.tex`
- `architecture/documenting-software-architecture/capturingthe-right-stakeholdersand-concerns.tex`
- `architecture/documenting-software-architecture/client-server-style.tex`
- `architecture/documenting-software-architecture/cloud-governance-control-framework-architecture.tex`
- `architecture/documenting-software-architecture/component-and-connector-views.tex`
- `architecture/documenting-software-architecture/confluence-space-structureand-directory-rationale.tex`
- `architecture/documenting-software-architecture/context-diagram.tex`
- `architecture/documenting-software-architecture/context-viewpoint.tex`
- `architecture/documenting-software-architecture/data-model-style.tex`
- `architecture/documenting-software-architecture/decomposition-style.tex`
- `architecture/documenting-software-architecture/deployment-style.tex`
- `architecture/documenting-software-architecture/designer-viewpoint.tex`
- `architecture/documenting-software-architecture/development-viewpoint.tex`
- `architecture/documenting-software-architecture/do-dafand-viewsand-beyond.tex`
- `architecture/documenting-software-architecture/element-catalog.tex`
- `architecture/documenting-software-architecture/generalization-style.tex`
- `architecture/documenting-software-architecture/information-viewpoint.tex`
- `architecture/documenting-software-architecture/install-style.tex`
- `architecture/documenting-software-architecture/interface-documentation.tex`
- `architecture/documenting-software-architecture/iso42010information-requirement-viewsand-beyond-location.tex`
- `architecture/documenting-software-architecture/layered-style.tex`
- `architecture/documenting-software-architecture/logical-viewpoint.tex`
- `architecture/documenting-software-architecture/module-views.tex`
- `architecture/documenting-software-architecture/operational-viewpoint.tex`
- `architecture/documenting-software-architecture/owner-viewpoint.tex`
- `architecture/documenting-software-architecture/peer-to-peer-style.tex`
- `architecture/documenting-software-architecture/pipe-and-filter-style.tex`
- `architecture/documenting-software-architecture/planner-viewpoint.tex`
- `architecture/documenting-software-architecture/primary-presentation.tex`
- `architecture/documenting-software-architecture/process-viewpoint.tex`
- `architecture/documenting-software-architecture/publish-subscribe-style.tex`
- `architecture/documenting-software-architecture/rationale.tex`
- `architecture/documenting-software-architecture/relating-viewsand-beyondto-rup.tex`
- `architecture/documenting-software-architecture/relating-viewsand-beyondtothe-rozanskiand-woodsviewpointset.tex`
- `architecture/documenting-software-architecture/reviewingfor-conformanceto-isoiec42010.tex`
- `architecture/documenting-software-architecture/rozanskiwoodsviewsandbeyond.tex`
- `architecture/documenting-software-architecture/rupviewsandbeyond.tex`
- `architecture/documenting-software-architecture/service-oriented-architecture-style.tex`
- `architecture/documenting-software-architecture/shared-data-style.tex`
- `architecture/documenting-software-architecture/spectrumof-style-specializations.tex`
- `architecture/documenting-software-architecture/stakeholder-documentation-needs-2.tex`
- `architecture/documenting-software-architecture/stakeholder-documentation-needs.tex`
- `architecture/documenting-software-architecture/supporting-development.tex`
- `architecture/documenting-software-architecture/supporting-evaluation.tex`
- `architecture/documenting-software-architecture/uses-style.tex`
- `architecture/documenting-software-architecture/variability-guide.tex`
- `architecture/documenting-software-architecture/variation-points.tex`
- `architecture/documenting-software-architecture/viewpointtemplate-2.tex`
- `architecture/documenting-software-architecture/viewpointtemplate.tex`
- `architecture/documenting-software-architecture/work-assignment-style.tex`
- `architecture/enterprise/enterprise-architecture-curriculum-2.tex`
- `architecture/enterprise/enterprise-architecture-curriculum.tex`
- `architecture/enterprise/main.tex`
- `architecture/system-design/build-system-facade-pattern.tex`
- `architecture/systems-engineering/main.tex`
- `architecture/systems-engineering/systems-curriculum.tex`
- `architecture/togaf/main.tex`
- `architecture/togaf/togafuser-stories.tex`
- `architecture/togaf/user-stories.tex`

### cloud

- `cloud/architecture/cloud-computing-book-mapping.tex`
- `cloud/finops/cloud-finops-curriculum.tex`
- `cloud/finops/cloud-finops-program-roadmap.tex`

### data-systems

- `data-systems/kafka/kafka-user-stories.tex`
- `data-systems/llm/llm-design-patterns-study-plan-template.tex`
- `data-systems/llm/user-stories.tex`

### devops

- `devops/ci-cd/analyze-sdlc.tex`
- `devops/ci-cd/cicdpipelinewith16gates.tex`
- `devops/ci-cd/ci-toolkit.tex`
- `devops/ci-cd/explore-git-hub.tex`
- `devops/ci-cd/git.tex`
- `devops/ci-cd/quick-start-git-hub-to-aws-app-runner.tex`
- `devops/ci-cd/release-engineering-quick-start.tex`
- `devops/github-actions/actions-custom-actions-quick-start.tex`
- `devops/github-actions/actions-inputs-env-secrets-artifacts.tex`
- `devops/github-actions/advanced-git-hub-actions.tex`
- `devops/github-actions/cicdstarter.tex`
- `devops/github-actions/controlling-job-executionin-git-hub-actions.tex`
- `devops/github-actions/custom-action-challenge.tex`
- `devops/github-actions/git-hub-actionsfora-wasmcpp-game.tex`
- `devops/github-actions/git-hub-actions-practical-cheat-sheet.tex`
- `devops/github-actions/git-hub-actions-quick-reference-workflow-action-attributes.tex`
- `devops/github-actions/git-hub-actions-workflows.tex`
- `devops/github-actions/minimal-git-hub-actionsfora-wasm-c-game.tex`
- `devops/github-actions/workflows-in-git-hub-actions.tex`
- `devops/github/collaboratingwith-your-communityon-git-hub.tex`
- `devops/github/github-enforcement-guide.tex`
- `devops/github/github-pr-at-scale-playbook.tex`
- `devops/github/git-hub-profile.tex`
- `devops/github/git-hub-releases-practical-quick-reference.tex`
- `devops/github/repository-setup-guide.tex`
- `devops/gitops/git-ops-stack-blueprint.tex`
- `devops/hashicorp-vault/vault-dev-server.tex`
- `devops/hashicorp-vault/vault-httpapiwith-postman.tex`
- `devops/hashicorp-vault/vault-production-style.tex`
- `devops/hashicorp-vault/vault-secrets-access-primer.tex`
- `devops/hashicorp-vault/vault-secure-introduction.tex`
- `devops/kubernetes/k8s-sequenced-stories.tex`
- `devops/nginx/nginx-cookbook-user-stories.tex`
- `devops/nginx/nginxcookbook-user-stories.tex`
- `devops/nginx/user-stories.tex`

### electronics

- `electronics/aoe-circuit-simulator-roadmap.tex`
- `electronics/electronics-curriculum.tex`
- `electronics/main-2.tex`
- `electronics/main.tex`
- `electronics/x-chapters-lab-course.tex`

### game-development

- `game-development/animation/computer-animation-user-stories.tex`
- `game-development/asset-pipelines/ai-assisted3dmodel-generation-pipeline.tex`
- `game-development/asset-pipelines/aisprite-generation-pipeline.tex`
- `game-development/design-documents/gdd-template.tex`
- `game-development/design-documents/main.tex`
- `game-development/graphics/cgpp-user-stories-template.tex`
- `game-development/physics/physics-engine-gap-analysis.tex`
- `game-development/webgl-wasm/user-stories.tex`

### mathematics

- `mathematics/algebra/how-matricesand-polynomials-relateto-algebraic-operations.tex`
- `mathematics/algebra/polynomial-data-structuresin-cand-c.tex`
- `mathematics/calculus/handbook-of-calculus-user-stories.tex`
- `mathematics/calculus/taocp-nr-study-deck.tex`
- `mathematics/geometry/cgc-study-plan-user-stories-2.tex`
- `mathematics/geometry/cgc-study-plan-user-stories.tex`
- `mathematics/geometry/dcg-study-plan-user-stories.tex`
- `mathematics/geometry/hdcg-study-plan-user-stories.tex`
- `mathematics/geometry/main.tex`
- `mathematics/geometry/polygon-data-structuresin-cand-c.tex`

### media

- `media/fast-channels/fast-animation-channels-programming-bible-2.tex`
- `media/fast-channels/fast-animation-channels-programming-bible.tex`
- `media/fast-channels/main.tex`

### personal

- `personal/finance/algo-trading-plan.tex`
- `personal/finance/cd-guide-2.tex`
- `personal/finance/cd-guide.tex`
- `personal/hobbies/locks-safes-security-study-plan-user-stories.tex`
- `personal/recipes/baguette.tex`
- `personal/recipes/beef-stew.tex`
- `personal/recipes/biscuits.tex`
- `personal/recipes/chef-salad.tex`
- `personal/recipes/chicken-curry.tex`
- `personal/recipes/chicken-parmesan.tex`
- `personal/recipes/chicken-tortilla-soup.tex`
- `personal/recipes/chilli.tex`
- `personal/recipes/cinnamon-rolls.tex`
- `personal/recipes/cioppino-fishermans-stew.tex`
- `personal/recipes/cioppino-seafood-stew-2.tex`
- `personal/recipes/cioppino-seafood-stew.tex`
- `personal/recipes/cobb-salad.tex`
- `personal/recipes/creamy-potato-celery-soup.tex`
- `personal/recipes/creamy-vegetable-soup-2.tex`
- `personal/recipes/creamy-vegetable-soup.tex`
- `personal/recipes/eggplant-parmesan.tex`
- `personal/recipes/grilled-shrimp-kabobs.tex`
- `personal/recipes/indian-chicken-curry-murgh-kari.tex`
- `personal/recipes/irish-vegetable-soup.tex`
- `personal/recipes/main-2.tex`
- `personal/recipes/main-3.tex`
- `personal/recipes/main-4.tex`
- `personal/recipes/main.tex`
- `personal/recipes/new-york-style-bagel.tex`
- `personal/recipes/peanut-butter-cheesecake.tex`
- `personal/recipes/roasted-celeryand-potato-soup.tex`
- `personal/recipes/seafood-gumbo.tex`
- `personal/recipes/seafood-stewwith-shrimpand-lobster.tex`
- `personal/recipes/shrimp-po-boys-2.tex`
- `personal/recipes/shrimp-po-boys.tex`
- `personal/recipes/southwest-salad-2.tex`
- `personal/recipes/southwest-salad.tex`
- `personal/recipes/vegetable-soup-2.tex`
- `personal/recipes/vegetable-soup.tex`
- `personal/recipes/zucchini-soup-2.tex`
- `personal/recipes/zucchini-soup.tex`

### physics-simulation

- `physics-simulation/fluid-simulation-curriculum-2.tex`
- `physics-simulation/fluid-simulation-curriculum.tex`
- `physics-simulation/main.tex`

### programming

- `programming/c-cpp/benefitsof-simulating-object-oriented-programmingin-cfor-embedded-systems.tex`
- `programming/typescript/effective-type-script-user-stories.tex`
- `programming/typescript/type-script-cookbook-user-stories.tex`
- `programming/web-frontend/design-of-sites-study-plan-user-stories.tex`
- `programming/web-frontend/designof-sites-user-stories.tex`
- `programming/web-frontend/mezzalira-micro-frontends-study-plan-story-cards.tex`
- `programming/web-frontend/user-stories-2.tex`
- `programming/web-frontend/user-stories.tex`

### security

- `security/appsec/application-security-program-ghas.tex`
- `security/appsec/application-security-program-roadmap.tex`
- `security/appsec/application-security-program.tex`
- `security/appsec/appsec-architecture-backlog.tex`
- `security/appsec/appsec-automation-ghas.tex`
- `security/appsec/appsec-certification-guide.tex`
- `security/appsec/appsec-course-priority-sequence.tex`
- `security/appsec/appsec-reading-sequence.tex`
- `security/appsec/app-sec-user-stories-resequenced.tex`
- `security/appsec/app-sec-user-stories.tex`
- `security/appsec/mappingthe-five-app-sec-core-processestoa16-gate-cicdpipeline0.tex`
- `security/appsec/modeling-application-security-processes.tex`
- `security/appsec/programs-and-systems.tex`
- `security/appsec/security-policies-github.tex`
- `security/appsec/user-stories.tex`
- `security/certifications/cish/cish4e-study-plan-story-cards-template-2.tex`
- `security/certifications/cish/cish4e-study-plan-story-cards-template.tex`
- `security/certifications/ciso/cisouser-stories.tex`
- `security/certifications/cissp/cisspuser-stories.tex`
- `security/cloud-security/cloud-computing-security-user-stories-aws.tex`
- `security/cloud-security/cloud-computing-security-user-stories-resequenced.tex`
- `security/cloud-security/cloud-computing-security-user-stories.tex`
- `security/cloud-security/secure-internal-apps-guide.tex`
- `security/cloud-security/secure-internet-facing-apps-guide.tex`
- `security/ghas/administring-ghas.tex`
- `security/ghas/applying-codeql-scanning.tex`
- `security/ghas/code-qlcapabilities.tex`
- `security/ghas/codeql-cheatsheet.tex`
- `security/ghas/codeql-triage-sop.tex`
- `security/ghas/code-scanning-cheatsheet.tex`
- `security/ghas/dependabot-alerts.tex`
- `security/ghas/dependabot-cheatsheet.tex`
- `security/ghas/enable-secret-protection-secret-scanning-alertsfora-git-hub-repository.tex`
- `security/ghas/external-scanning-sarif-upload.tex`
- `security/ghas/ghas-cheatsheet.tex`
- `security/ghas/ghas-dependabot-cheatsheet-2.tex`
- `security/ghas/ghas-dependabot-cheatsheet.tex`
- `security/ghas/ghas-documentation-roadmap.tex`
- `security/ghas/ghas-secret-scanning-cheat-sheet.tex`
- `security/ghas/ghas-secret-scanning-sop.tex`
- `security/ghas/ghas-secret-scanning-triage-sop.tex`
- `security/ghas/ghas-study-plan-user-stories.tex`
- `security/ghas/git-hub-advanced-security-ghasand-its-roleina16-gate-cicdpipeline.tex`
- `security/ghas/git-hub-advanced-security-ghasbest-practices.tex`
- `security/ghas/git-hub-code-scanning-quickstart.tex`
- `security/ghas/notification-decision-matrixfor-monitoring-secret-scanning-alerts.tex`
- `security/ghas/role-scope-access-matrixfor-metricsfor-custom-patterns.tex`
- `security/ghas/secret-scanning-triage-sequence.tex`
- `security/ghas/secret-scanning-triage-sop.tex`
- `security/ghas/servicenow-ghas-integration-blueprint.tex`
- `security/ghas/viewingandfilteringalertsfromsecretscanning.tex`
- `security/owasp/a012025-broken-access-control.tex`
- `security/owasp/a022025-security-misconfiguration.tex`
- `security/owasp/a032025-software-supply-chain-failures.tex`
- `security/owasp/a042025-cryptographic-failures.tex`
- `security/owasp/a052025-injection.tex`
- `security/owasp/a062025-insecure-design.tex`
- `security/owasp/a072025-authentication-failures.tex`
- `security/owasp/a082025-softwareor-data-integrity-failures.tex`
- `security/owasp/a092025-security-logging-alerting-failures.tex`
- `security/owasp/a102025-mishandlingof-exceptional-conditions.tex`
- `security/owasp/owaspapisecurity-top10.tex`
- `security/owasp/user-stories.tex`

### uncategorized

- `uncategorized/practical-overviewof-git-hub-advanced-security.tex`

