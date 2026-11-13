#!/usr/bin/env node
/** Deterministic source-file inventory. Does not execute grammar factories. */
import { readFileSync } from "node:fs";
import { resolve, dirname } from "node:path";
import { fileURLToPath } from "node:url";

const root = resolve(dirname(fileURLToPath(import.meta.url)), "..");
export const sources = Object.freeze([
  { id: "ecmascript-2025", module: "es2025Grammar.ts", sourceFactories: 261, expectedFactories: 261, expectedDefinitions: 261 },
  { id: "cpp23", module: "cppGrammar.ts", sourceFactories: 351, expectedFactories: 351, expectedDefinitions: 351 },
  { id: "c23", module: "c23Grammar.ts", sourceFactories: 94, expectedFactories: 96, expectedDefinitions: 96, upstreamMissingFactories: ["argument-expression-list", "compound-literal"] },
  { id: "java-25", module: "java25Grammar.ts", sourceFactories: 253, expectedFactories: 253, expectedDefinitions: 253 },
  { id: "python-314", module: "pythonGrammar.ts", sourceFactories: 205, expectedFactories: 205, expectedDefinitions: 205 }
]);
function collect(regex, data) { return [...data.matchAll(regex)].map(match => match[1]); }
function duplicates(names) {
  const seen = new Set(), repeated = new Set();
  for (const name of names) { if (seen.has(name)) repeated.add(name); seen.add(name); }
  return [...repeated].sort();
}
export function collectInventory() {
  return sources.map(source => {
    const dir = resolve(root, "src", "grammars", source.id);
    const grammar = readFileSync(resolve(dir, source.module), "utf8");
    const ebnf = readFileSync(resolve(dir, "ebnfDefinitions.ts"), "utf8");
    const diagramNames = collect(/rules\.set\(\s*["']([^"']+)["']/g, grammar);
    const definitionNames = collect(/^\s*["']([^"']+)["']\s*:/gm, ebnf);
    const listed = grammar.split("export const SECTION_RULES")[1]?.split(/\n\};/)[0] ?? "";
    const sectionMatches = [...listed.matchAll(/^\s*(?:["']([^"']+)["']|([a-zA-Z_]\w*))\s*:\s*\[([\s\S]*?)\]/gm)];
    const sections = sectionMatches.map(m => ({ id: m[1] ?? m[2], rules: collect(/["']([^"']+)["']/g, m[3]) }));
    const diagramSet = new Set(diagramNames), definitionSet = new Set(definitionNames);
    const navigationNames = sections.flatMap(section => section.rules), navSet = new Set(navigationNames);
    return {
      id: source.id, grammarModule: source.module, sourceFactoryCount: source.sourceFactories,
      diagramCount: diagramSet.size, definitionCount: definitionSet.size, sectionCount: sections.length,
      diagramRuleNames: [...diagramSet].sort(), definitionRuleNames: [...definitionSet].sort(),
      duplicateDiagrams: duplicates(diagramNames), duplicateDefinitions: duplicates(definitionNames),
      duplicateNavigation: duplicates(navigationNames),
      missingDefinitions: [...diagramSet].filter(name => !definitionSet.has(name)).sort(),
      missingDiagrams: [...definitionSet].filter(name => !diagramSet.has(name)).sort(),
      unlistedDiagrams: [...diagramSet].filter(name => !navSet.has(name)).sort(),
      navigationWithoutDiagram: [...navSet].filter(name => !diagramSet.has(name)).sort()
    };
  });
}
if (process.argv[1] && resolve(process.argv[1]) === fileURLToPath(import.meta.url)) {
  console.log(JSON.stringify(collectInventory(), null, 2));
}
