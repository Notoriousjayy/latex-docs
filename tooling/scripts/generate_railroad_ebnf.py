#!/usr/bin/env python3
"""Convert pinned railroad factory expressions to native PlantUML EBNF diagrams.

This is a build-time converter, not an imported React application. Each rule
generates one .puml file; the existing pinned PlantUML renderer produces PNG.
Source-specific semantic actions and PEG predicates cannot be assumed to carry
over. Unsupported factory expressions receive an explicitly marked schematic
diagram and the complete original text remains visible in the Pages gallery.
"""
from __future__ import annotations

import argparse
import ast
import json
import re
from collections import Counter
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
COLLECTION = ROOT / "src/programming/languages/syntax-diagrams"
DEFAULT_OUTPUT = COLLECTION / "railroad-generated"
LANGUAGES = (
    ("ecmascript-2025", "ECMAScript 2025"),
    ("cpp23", "C++23"),
    ("c23", "C23"),
    ("java-25", "Java 25"),
    ("python-314", "Python 3.14"),
)
CHUNK_SIZE = 25
RULE_RE = re.compile(r'rules\s*\.\s*set\s*\(\s*"([^"]+)"\s*,')
CALL_RE = re.compile(r'\b(?:Diagram|D)\s*\(')
RETURN_RE = re.compile(r'\breturn\s+(?:Diagram|D)\s*\(')
CONST_RE = re.compile(r'\bconst\s+([A-Za-z_]\w*)\s*=')
LEXER = re.compile(
    r'\s+|//[^\n]*|/\*.*?\*/|"(?:\\.|[^"\\])*"|'
    r"'(?:\\.|[^'\\])*'|[A-Za-z_$][\w$]*|\d+|=>|\.{3}|.",
    re.DOTALL,
)


def source_data(language: str) -> dict:
    path = COLLECTION / "data" / (language + ".json")
    data = json.loads(path.read_text(encoding="utf-8"))
    if data.get("language") != language:
        raise ValueError("Grammar identity mismatch: " + language)
    if not data.get("sourceRevision") or len(data["sourceRevision"]) != 40:
        raise ValueError("Grammar is not pinned to a source revision")
    names = [rule["name"] for rule in data["rules"]]
    if len(names) != len(set(names)):
        raise ValueError("Duplicate grammar names in " + language)
    return data


def grammar_parts(source: str) -> dict[str, str]:
    matches = list(RULE_RE.finditer(source))
    return {
        item.group(1): source[item.end(): matches[i + 1].start() if i + 1 < len(matches) else len(source)]
        for i, item in enumerate(matches)
    }


def tokens(code: str) -> list[str]:
    out = []
    for match in LEXER.finditer(code):
        item = match.group()
        if item.isspace() or item.startswith("//") or item.startswith("/*"):
            continue
        out.append(item)
    return out


def string_value(literal: str) -> str:
    if literal.startswith('"'):
        try:
            return json.loads(literal)
        except (ValueError, json.JSONDecodeError):
            pass
    try:
        return ast.literal_eval(literal)
    except (ValueError, SyntaxError):
        return literal[1:-1]


@dataclass
class Node:
    kind: str
    args: list
    value: str = ""


class ExprParser:
    def __init__(self, lexemes: list[str]):
        self.parts = lexemes
        self.i = 0

    def at(self) -> str:
        return self.parts[self.i] if self.i < len(self.parts) else ""

    def pop(self) -> str:
        value = self.at()
        self.i += 1
        return value

    def parse(self) -> Node:
        token = self.pop()
        if not token:
            raise ValueError("empty syntax factory expression")
        if token == "...":
            return Node("spread", [self.parse()])
        if token == "(":
            result = self.parse()
            if self.pop() != ")":
                raise ValueError("unbalanced parenthesis")
            return result
        if token == "[":
            children = self.arguments("]")
            return Node("array", children)
        if token[0] in "'\"" and len(token) > 1:
            return Node("string", [], string_value(token))
        if token.isdigit():
            return Node("number", [], token)
        if re.fullmatch(r"[A-Za-z_$][\w$]*", token):
            # Helper calls are composable; unsupported methods become explicit
            # conversion gaps instead of guessed grammar semantics.
            name = token
            while self.at() == ".":
                self.pop()
                name += "." + self.pop()
            if self.at() == "(":
                self.pop()
                return Node(name, self.arguments(")"))
            return Node("variable", [], name)
        return Node("unknown", [], token)

    def arguments(self, terminator: str) -> list[Node]:
        out = []
        while self.at() and self.at() != terminator:
            if self.at() == ",":
                self.pop()
                continue
            position = self.i
            out.append(self.parse())
            if self.i == position:
                raise ValueError("non-advancing expression parser")
            if self.at() not in (",", terminator):
                raise ValueError("unsupported operator near " + self.at())
        if self.pop() != terminator:
            raise ValueError("unclosed expression")
        return out


def sanitize_id(name: str) -> str:
    value = re.sub(r"[^A-Za-z0-9_]", "_", name)
    if not value or not re.match(r"[A-Za-z_]", value):
        value = "rule_" + value
    return value


def terminal(value: str) -> str:
    # Conservative EBNF quoting; the exact spelling is retained on the page.
    out = []
    for char in value:
        if char == '"':
            out.append("[double quote]")
        elif char == "\\":
            out.append("[backslash]")
        elif ord(char) < 32 or ord(char) > 126:
            out.append("[U+" + format(ord(char), "04X") + "]")
        else:
            out.append(char)
    return '"' + "".join(out) + '"'


def compile_node(node: Node, bindings: dict[str, Node], depth: int = 0) -> str:
    if depth > 60:
        raise ValueError("grammar expression recursion limit")
    kind = node.kind
    args = node.args
    compile_child = lambda child: compile_node(child, bindings, depth + 1)
    if kind == "variable":
        if node.value in bindings:
            return compile_child(bindings[node.value])
        raise ValueError("unknown grammar helper: " + node.value)
    if kind == "string":
        return terminal(node.value)
    if kind in ("T", "Terminal"):
        if len(args) != 1 or args[0].kind != "string":
            raise ValueError("dynamic terminal")
        return terminal(args[0].value)
    if kind in ("NT", "NonTerminal"):
        if len(args) != 1 or args[0].kind != "string":
            raise ValueError("dynamic nonterminal")
        return sanitize_id(args[0].value)
    if kind in ("Comment", "Cmt"):
        return terminal("[note] " + (args[0].value if args and args[0].kind == "string" else "See textual grammar"))
    if kind in ("Diagram", "D", "Sequence", "Seq", "Stack"):
        return ", ".join(compile_child(x) for x in args) if args else terminal("empty")
    if kind in ("Choice", "Ch"):
        alternatives = args[1:] if args and args[0].kind == "number" else args
        if not alternatives:
            raise ValueError("empty choice")
        return "(" + " | ".join(compile_child(x) for x in alternatives) + ")"
    if kind in ("Optional", "Opt"):
        return "[ " + ", ".join(compile_child(x) for x in args) + " ]"
    if kind in ("ZeroOrMore", "ZOM"):
        return "{ " + ", ".join(compile_child(x) for x in args) + " }"
    if kind in ("OneOrMore", "OOM"):
        if not args:
            raise ValueError("empty repetition")
        first = compile_child(args[0])
        if len(args) > 1:
            return "( " + first + ", { " + compile_child(args[1]) + ", " + first + " } )"
        return "( " + first + ", { " + first + " } )"
    if kind == "chain":
        if len(args) != 2 or args[0].kind != "string" or args[1].kind != "array":
            raise ValueError("unexpected precedence chain shape")
        base = sanitize_id(args[0].value)
        ops = [terminal(x.value) for x in args[1].args if x.kind == "string"]
        if not ops:
            raise ValueError("empty chain operators")
        return base + ", { ( " + " | ".join(ops) + " ), " + base + " }"
    raise ValueError("unsupported factory construct: " + kind)


def rule_expression(body: str) -> tuple[str, str]:
    bindings: dict[str, Node] = {}
    for item in CONST_RE.finditer(body):
        try:
            bindings[item.group(1)] = ExprParser(tokens(body[item.end():])).parse()
        except (ValueError, IndexError):
            pass
    root = RETURN_RE.search(body) or CALL_RE.search(body)
    if root is None:
        raise ValueError("no diagram factory expression")
    start = body.index("Diagram", root.start()) if "Diagram" in root.group() else body.index("D(", root.start())
    tree = ExprParser(tokens(body[start:])).parse()
    return compile_node(tree, bindings), "factory-derived"


def rule_path(language: str, index: int, name: str) -> Path:
    slug = re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")[:70] or "rule"
    folder = "part-" + format((index - 1) // CHUNK_SIZE + 1, "03d")
    return Path(language) / folder / (format(index, "04d") + "-" + slug + ".puml")


def build_rule(language: str, name: str, body: str | None) -> tuple[str, str]:
    mode = "factory-derived"
    try:
        if body is None:
            raise ValueError("text-only upstream production")
        expression, mode = rule_expression(body)
        if len(expression) > 3500:
            raise ValueError("production too large for validated EBNF conversion")
    except (ValueError, IndexError, RecursionError):
        # Honest fallback: do not invent grammar syntax when conversion is
        # unsupported. The complete authoritative transcription is on the page.
        expression = terminal("See complete source production below")
        mode = "text-only"
    title = sanitize_id(name)
    content = (
        "@startebnf\n"
        + "(* Source: " + language + "; rule " + format(len(name), "d") + " character identifier. *)\n"
        + title + " = " + expression + ";\n"
        + "@endebnf\n"
    )
    return content, mode


def generate(output_dir: Path, limit_per_language: int = 0, check_only: bool = False) -> dict:
    result = {"total": 0, "modes": Counter(), "languages": {}}
    for language, title in LANGUAGES:
        data = source_data(language)
        module = COLLECTION / "data/upstream" / (language + "-factory-source.txt")
        factories = grammar_parts(module.read_text(encoding="utf-8"))
        if len(factories) != data["sourceFactoryCount"]:
            raise ValueError("Upstream factory count changed for " + language)
        entries = data["rules"][:limit_per_language] if limit_per_language else data["rules"]
        counts: Counter = Counter()
        for index, entry in enumerate(entries, 1):
            rule = entry["name"]
            diagram, mode = build_rule(language, rule, factories.get(rule))
            relative = rule_path(language, index, rule)
            if not check_only:
                target = output_dir / relative
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_text(diagram, encoding="utf-8")
            counts[mode] += 1
            result["modes"][mode] += 1
            result["total"] += 1
        result["languages"][language] = {"display_name": title, "count": len(entries), "modes": dict(counts)}
    result["modes"] = dict(result["modes"])
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--check-only", action="store_true")
    parser.add_argument("--limit-per-language", type=int, default=0)
    parser.add_argument("--manifest", type=Path)
    args = parser.parse_args()
    if args.limit_per_language < 0:
        parser.error("--limit-per-language cannot be negative")
    output_dir = args.output_dir.resolve()
    if not args.check_only:
        if output_dir.exists():
            import shutil
            shutil.rmtree(output_dir)
        output_dir.mkdir(parents=True)
    report = generate(output_dir, args.limit_per_language, args.check_only)
    if not args.limit_per_language and report["total"] != 1166:
        raise ValueError("All 1,166 grammar productions must be accounted for")
    if args.manifest:
        args.manifest.parent.mkdir(parents=True, exist_ok=True)
        args.manifest.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
