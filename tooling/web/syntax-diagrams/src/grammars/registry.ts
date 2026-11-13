import * as es from "./ecmascript-2025/es2025Grammar";
import { EBNF_DEFINITIONS as esText } from "./ecmascript-2025/ebnfDefinitions";
import * as cpp from "./cpp23/cppGrammar";
import { EBNF_DEFINITIONS as cppText } from "./cpp23/ebnfDefinitions";
import * as c from "./c23/c23Grammar";
import { EBNF_DEFINITIONS as cText } from "./c23/ebnfDefinitions";
import * as java from "./java-25/java25Grammar";
import { EBNF_DEFINITIONS as javaText } from "./java-25/ebnfDefinitions";
import * as python from "./python-314/pythonGrammar";
import { EBNF_DEFINITIONS as pythonText } from "./python-314/ebnfDefinitions";

export interface GrammarSection {
  id: string;
  title: string;
  rules: readonly string[];
}
export interface GrammarSpec {
  id: string;
  title: string;
  version: string;
  notation: string;
  specification: string;
  sourceRepository: string;
  sourceCommit: string;
  sections: readonly GrammarSection[];
  definitions: Readonly<Record<string, string>>;
  ruleNames: () => string[];
  diagram: (rule: string) => any;
}

export const grammars: GrammarSpec[] = [
  {
    id: "ecmascript-2025", title: "ECMAScript 2025", version: "ECMA-262 (2025)",
    notation: "ECMAScript lexical and syntactic grammars (diagram-friendly transcription)",
    specification: "https://tc39.es/ecma262/",
    sourceRepository: "Notoriousjayy/JavaScript-Syntax-diagrams",
    sourceCommit: "29725abeb6010e9b2bf7669010a0addcd07b32e7",
    sections: es.SECTION_ORDER.map(id => ({ id, title: es.SECTION_TITLES[id], rules: es.SECTION_RULES[id] })),
    definitions: esText, ruleNames: es.getDiagramRuleNames, diagram: es.createRuleDiagram
  },
  {
    id: "cpp23", title: "C++23", version: "ISO/IEC 14882:2024",
    notation: "C++ grammar summary (diagram-friendly transcription)",
    specification: "https://eel.is/c++draft/gram",
    sourceRepository: "Notoriousjayy/Cpp23-Syntax-diagrams",
    sourceCommit: "b546b5b0c79cbcf304e2232a4e61b871b825b599",
    sections: cpp.SECTION_ORDER.map(id => ({ id, title: cpp.SECTION_TITLES[id], rules: cpp.SECTION_RULES[id] })),
    definitions: cppText, ruleNames: cpp.getRuleNames, diagram: cpp.createRuleDiagram
  },
  {
    id: "c23", title: "C23", version: "ISO/IEC 9899:2024",
    notation: "C grammar subset (diagram-friendly transcription)",
    specification: "https://www.iso.org/standard/82075.html",
    sourceRepository: "Notoriousjayy/c23-syntax-diagrams",
    sourceCommit: "11e9a6995e30f3327225d8241c28c5f5d06e7830",
    sections: c.SECTION_ORDER.map(id => ({ id, title: c.SECTION_TITLES[id], rules: c.SECTION_RULES[id] })),
    definitions: cText, ruleNames: c.getRuleNames, diagram: c.createRuleDiagram
  },
  {
    id: "java-25", title: "Java 25", version: "Java SE 25 (JLS)",
    notation: "Java Language Specification grammar (Chapter 19)",
    specification: "https://docs.oracle.com/javase/specs/jls/se25/html/jls-19.html",
    sourceRepository: "Notoriousjayy/java21-syntax-diagrams",
    sourceCommit: "177088bf881aaca4f0406d90f88d5b04d3ad7c84",
    sections: java.SECTION_ORDER.map(id => ({ id, title: java.SECTION_TITLES[id], rules: java.SECTION_RULES[id] })),
    definitions: javaText, ruleNames: java.getDiagramRuleNames, diagram: java.createRuleDiagram
  },
  {
    id: "python-314", title: "Python 3.14", version: "Python 3.14",
    notation: "PEG-based grammar; textual transcription is not a semantics-preserving EBNF conversion",
    specification: "https://docs.python.org/3.14/reference/grammar.html",
    sourceRepository: "Notoriousjayy/Python-syntax-diagrams",
    sourceCommit: "d42d1ead4e1cf94149943a4cf8ea79f0dd96eaef",
    sections: python.SECTION_ORDER.map(id => ({ id, title: python.SECTION_TITLES[id], rules: python.SECTION_RULES[id] })),
    definitions: pythonText, ruleNames: python.getRuleNames, diagram: python.createRuleDiagram
  }
];

export function findGrammar(id: string): GrammarSpec {
  return grammars.find(grammar => grammar.id === id) ?? grammars[0];
}
