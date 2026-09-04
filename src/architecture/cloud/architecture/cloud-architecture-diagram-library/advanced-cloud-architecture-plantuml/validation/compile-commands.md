# Compilation

Each diagram in this set is self-contained and compiles independently. No `!include` directives are used, so files can be moved or compiled in isolation.

## Requirements

- Java 8 or later (validated with OpenJDK 21).
- The repository-pinned PlantUML jar. Run `make render-plantuml` from the repository root; do not use the distribution `plantuml` package.

## Compile all diagrams to PNG

    make render-plantuml

## Compile all diagrams to SVG

    make render-plantuml

## Compile a single diagram

    JAR="$(python3 tooling/scripts/latex_build.py fetch-plantuml)"
    java -Djava.awt.headless=true -jar "$JAR" -tsvg -failfast2 diagrams/01_hypervisor_clustering.puml

## Compile to a separate output directory

    JAR="$(python3 tooling/scripts/latex_build.py fetch-plantuml)"
    java -Djava.awt.headless=true -jar "$JAR" -tsvg -failfast2 -o ./out diagrams/*.puml

## Notes

- Output files are written next to each input `.puml` unless `-o` is specified.
- The diagrams use only built-in PlantUML constructs and a small set of `skinparam` directives. No external themes or stylesheets are referenced.
- Each `.puml` file passes a clean compile with the manifest-pinned engine.



