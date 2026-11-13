import { useEffect, useMemo, useState } from "react";
import { RuleList } from "../components/RuleList";
import { findGrammar, grammars } from "../grammars/registry";

function readRoute(): { language: string; rule: string | null } {
  const parts = window.location.hash.replace(/^#\/?/, "").split("/");
  const language = findGrammar(parts[0]).id;
  let rule: string | null = null;
  if (parts[1]) {
    try { rule = decodeURIComponent(parts.slice(1).join("/")); }
    catch { rule = null; }
  }
  return { language, rule };
}

export default function App() {
  const [route, setRoute] = useState(readRoute);
  const grammar = findGrammar(route.language);
  const [query, setQuery] = useState("");
  const [expanded, setExpanded] = useState<Set<string>>(() => new Set([grammar.sections[0].id]));

  useEffect(() => {
    const onHashChange = () => {
      const next = readRoute();
      setRoute(next);
      const selected = findGrammar(next.language);
      setExpanded(new Set(next.rule ? selected.sections.filter(s => s.rules.includes(next.rule!)).map(s => s.id) : [selected.sections[0].id]));
    };
    window.addEventListener("hashchange", onHashChange);
    return () => window.removeEventListener("hashchange", onHashChange);
  }, []);

  useEffect(() => {
    if (!route.rule) return;
    const node = document.getElementById("rule-" + route.language + "-" + route.rule);
    node?.scrollIntoView({ block: "start" });
  }, [route, expanded]);

  const chooseLanguage = (id: string) => {
    setQuery("");
    setRoute({ language: id, rule: null });
    setExpanded(new Set([findGrammar(id).sections[0].id]));
    window.location.hash = "/" + id;
  };

  const sections = useMemo(() => grammar.sections.map(section => ({
    ...section,
    filtered: section.rules.filter(name => name.toLowerCase().includes(query.trim().toLowerCase()))
  })), [grammar, query]);

  const toggle = (id: string) => {
    setExpanded(previous => {
      const next = new Set(previous);
      if (next.has(id)) next.delete(id); else next.add(id);
      return next;
    });
  };

  const crossLanguage = useMemo(() => grammars.map(item => ({
    ...item, matches: query.trim().length < 3 ? [] : item.ruleNames().filter(name => name.toLowerCase().includes(query.trim().toLowerCase()))
  })), [query]);

  return (
    <>
      <header>
        <div className="app-heading">
          <h1>Programming Language Syntax Diagrams</h1>
          <p className="subtitle">One application · five language specifications · preserved grammar provenance</p>
        </div>
        <div className="toolbar">
          <label htmlFor="language-choice">Language</label>
          <select id="language-choice" value={grammar.id} onChange={event => chooseLanguage(event.target.value)}>
            {grammars.map(item => <option value={item.id} key={item.id}>{item.title}</option>)}
          </select>
          <label htmlFor="grammar-query">Find production</label>
          <input id="grammar-query" type="search" value={query} onChange={event => setQuery(event.target.value)}
            placeholder="Search grammar rules by name" />
          <div className="toolbar-actions">
            <button className="toolbar-btn" onClick={() => setExpanded(new Set(grammar.sections.map(s => s.id)))}>Expand all</button>
            <button className="toolbar-btn" onClick={() => setExpanded(new Set())}>Collapse all</button>
          </div>
        </div>
        <p className="subtitle"><strong>{grammar.title}</strong> · {grammar.version} · {grammar.ruleNames().length} diagram factories · <a href={grammar.specification} rel="noreferrer" target="_blank">Language specification</a></p>
        <p className="subtitle">{grammar.notation}. Diagrams visualize productions; semantic restrictions may be additional.</p>
        <nav aria-label="Grammar sections">
          {grammar.sections.map(section => <a key={section.id} href={"#section-" + section.id}
            onClick={event => { event.preventDefault(); setExpanded(previous => new Set([...previous, section.id])); document.getElementById("section-" + section.id)?.scrollIntoView(); }}>
            {section.title}</a>)}
        </nav>
      </header>
      <main>
        {query.trim().length >= 3 && (
          <aside className="cross-search" aria-label="Cross-language name search">
            <strong>Cross-language rule-name matches</strong>
            <p>Matches are textual similarities, not assertions of equivalent language semantics.</p>
            <div className="cross-links">
              {crossLanguage.filter(item => item.matches.length).map(item => (
                <button className="toolbar-btn" key={item.id} onClick={() => chooseLanguage(item.id)}>{item.title}: {item.matches.length}</button>
              ))}
            </div>
          </aside>
        )}
        {sections.map(section => {
          if (query && !section.filtered.length) return null;
          const open = query.trim() ? section.filtered.length > 0 : expanded.has(section.id);
          return (
            <section key={grammar.id + section.id} className="grammar-section" id={"section-" + section.id}>
              <button className="section-header" aria-expanded={open}
                aria-controls={"section-content-" + section.id} onClick={() => toggle(section.id)}>
                <span className={"section-chevron " + (open ? "expanded" : "")}>▶</span>
                <h2>{section.title}</h2>
                <span className="rule-count">({section.filtered.length} rules)</span>
              </button>
              {open && <div className="section-content" id={"section-content-" + section.id}>
                <RuleList grammar={grammar} names={section.filtered} />
              </div>}
            </section>
          );
        })}
      </main>
      <footer>
        <p>Grammar source: <a href={"https://github.com/" + grammar.sourceRepository + "/tree/" + grammar.sourceCommit}>original repository at fixed revision</a>.
          Browse printable references in the <a href="https://github.com/Notoriousjayy/latex-docs/tree/main/src/programming/languages">LaTeX documentation library</a>.</p>
      </footer>
    </>
  );
}
