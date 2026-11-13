/** Render only locally defined, reviewed grammar factories. Never pass untrusted SVG here. */
export function diagramToSvgString(diagram: any): string {
  if (!diagram) return "";
  try {
    if (typeof diagram.toSVG === "function") {
      const svg = diagram.toSVG();
      if (typeof svg === "string") return svg;
      if (svg && typeof svg === "object" && "nodeType" in svg) {
        const element = svg as Element;
        return element.outerHTML ?? new XMLSerializer().serializeToString(element);
      }
    }
    if (typeof diagram.toString === "function") {
      const rendered = String(diagram.toString());
      if (rendered.includes("<svg")) return rendered;
    }
  } catch (error) {
    console.error("Railroad diagram rendering failed", error);
  }
  return "";
}
