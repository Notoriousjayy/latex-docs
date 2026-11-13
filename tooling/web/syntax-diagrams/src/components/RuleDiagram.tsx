import { useMemo } from "react";
import type { GrammarSpec } from "../grammars/registry";
import { diagramToSvgString } from "../shared/railroad/diagramToSvg";

export function RuleDiagram({ grammar, name }: { grammar: GrammarSpec; name: string }) {
  const svg = useMemo(() => diagramToSvgString(grammar.diagram(name)), [grammar, name]);
  const definition = grammar.definitions[name];
  const permalink = "#/" + grammar.id + "/" + encodeURIComponent(name);

  const download = () => {
    if (!svg) return;
    const blob = new Blob([svg], { type: "image/svg+xml;charset=utf-8" });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = grammar.id + "-" + name.replace(/[^a-zA-Z0-9_-]/g, "_") + ".svg";
    link.click();
    URL.revokeObjectURL(url);
  };

  return (
    <article className="rule" id={"rule-" + grammar.id + "-" + name}>
      <div className="rule-heading">
        <h3>{name}</h3>
        <a href={permalink} aria-label={"Permalink to " + name}>Link</a>
        {svg && <button className="toolbar-btn" onClick={download}>Export SVG</button>}
      </div>
      {svg ? <div className="svgwrap" dangerouslySetInnerHTML={{ __html: svg }} />
           : <p role="alert">Diagram unavailable for this production.</p>}
      {definition && (
        <details className="ebnf-container">
          <summary className="ebnf-toggle">Grammar definition</summary>
          <pre className="ebnf-code">{definition}</pre>
        </details>
      )}
    </article>
  );
}
