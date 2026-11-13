import test from "node:test";
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { resolve } from "node:path";
import { fileURLToPath } from "node:url";
import { collectInventory, sources } from "../scripts/grammar-inventory.mjs";

const root = resolve(fileURLToPath(new URL("..", import.meta.url)));
const data = collectInventory();

test("all five complete grammar modules are present", () => {
  assert.deepEqual(data.map(item => item.id), sources.map(item => item.id));
  assert.equal(data.reduce((total, item) => total + item.diagramCount, 0), 1166);
});
for (const row of data) {
  test(row.id + " grammar factories equal text and section navigation", () => {
    assert.equal(row.diagramCount, sources.find(item => item.id === row.id).expectedFactories);
    assert.deepEqual(row.missingDefinitions, []);
    assert.deepEqual(row.missingDiagrams, []);
    assert.deepEqual(row.unlistedDiagrams, []);
    assert.deepEqual(row.navigationWithoutDiagram, []);
    assert.deepEqual(row.duplicateDiagrams, []);
    assert.deepEqual(row.duplicateDefinitions, []);
    assert.deepEqual(row.duplicateNavigation, []);
    assert.ok(row.sectionCount > 0);
  });
}
test("registry preserves pinned revision and correct language identifiers", () => {
  const registry = readFileSync(resolve(root, "src/grammars/registry.ts"), "utf8");
  for (const source of sources) assert.ok(registry.includes('id: "' + source.id + '"'), source.id);
  assert.ok(registry.includes('id: "java-25"'));
  assert.ok(!registry.includes('id: "java-21"'));
});
