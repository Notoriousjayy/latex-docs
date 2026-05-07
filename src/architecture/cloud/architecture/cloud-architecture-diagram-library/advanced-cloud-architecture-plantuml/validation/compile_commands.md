# Compilation

Each diagram in this set is self-contained and compiles independently. No `!include` directives are used, so files can be moved or compiled in isolation.

## Requirements

- Java 8 or later (validated with OpenJDK 21).
- `plantuml.jar` (or a `plantuml` package binary). The set has been validated against PlantUML 1.2020.02; later versions also work.

## Compile all diagrams to PNG

    java -jar plantuml.jar -tpng diagrams/*.puml

## Compile all diagrams to SVG

    java -jar plantuml.jar -tsvg diagrams/*.puml

## Compile a single diagram

    java -jar plantuml.jar -tsvg diagrams/01_hypervisor_clustering.puml

## Compile to a separate output directory

    java -jar plantuml.jar -tsvg -o ./out diagrams/*.puml

## Using a packaged binary (Debian / Ubuntu)

    sudo apt-get install plantuml
    plantuml -tsvg diagrams/*.puml
    plantuml -tpng diagrams/*.puml

## Notes

- Output files are written next to each input `.puml` unless `-o` is specified.
- The diagrams use only built-in PlantUML constructs and a small set of `skinparam` directives. No external themes or stylesheets are referenced.
- Each `.puml` file passes a clean compile (no errors and no warnings) on PlantUML 1.2020.02.
