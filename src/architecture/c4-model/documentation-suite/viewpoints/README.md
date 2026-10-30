# Viewpoints

Seven reusable viewpoint specifications. These are neither individual project views nor ADRs.

## Files

- [`viewpoint-code.tex`](viewpoint-code.tex)
- [`viewpoint-component.tex`](viewpoint-component.tex)
- [`viewpoint-container.tex`](viewpoint-container.tex)
- [`viewpoint-context.tex`](viewpoint-context.tex)
- [`viewpoint-deployment.tex`](viewpoint-deployment.tex)
- [`viewpoint-dynamic.tex`](viewpoint-dynamic.tex)
- [`viewpoint-landscape.tex`](viewpoint-landscape.tex)

## Build and ownership

Files are standalone pdfLaTeX roots. Compile from this directory with `pdflatex -interaction=nonstopmode -halt-on-error FILE.tex`, or use the suite validator. Keep source provenance and independently authored extensions distinct.
