import type { GrammarSpec } from "../grammars/registry";
import { RuleDiagram } from "./RuleDiagram";

export function RuleList({ grammar, names }: { grammar: GrammarSpec; names: readonly string[] }) {
  return <>{names.map(name => <RuleDiagram key={name} grammar={grammar} name={name} />)}</>;
}
