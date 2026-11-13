#!/usr/bin/env node
import { collectInventory, sources } from "./grammar-inventory.mjs";

let failures = 0;
for (const inventory of collectInventory()) {
  const source = sources.find(item => item.id === inventory.id);
  if (!source) throw new Error("Unknown language: " + inventory.id);
  const problems = [
    ...inventory.missingDiagrams.map(rule => "missing factory: " + rule),
    ...inventory.missingDefinitions.map(rule => "missing text: " + rule),
    ...inventory.unlistedDiagrams.map(rule => "unlisted factory: " + rule),
    ...inventory.navigationWithoutDiagram.map(rule => "navigation has no factory: " + rule),
    ...inventory.duplicateDiagrams.map(rule => "duplicate factory: " + rule),
    ...inventory.duplicateDefinitions.map(rule => "duplicate definition: " + rule),
    ...inventory.duplicateNavigation.map(rule => "duplicate section registration: " + rule)
  ];
  if (inventory.diagramCount !== source.expectedFactories) problems.push("diagram count changed from migration baseline");
  if (inventory.definitionCount !== source.expectedDefinitions) problems.push("definition count changed from migration baseline");
  if (!inventory.sectionCount) problems.push("no registered sections");
  console.log(inventory.id + ": " + inventory.diagramCount + " diagrams, " + inventory.definitionCount +
    " definitions, " + inventory.sectionCount + " sections; " + (problems.length ? "FAIL" : "PASS"));
  for (const problem of problems) console.error("  - " + problem);
  failures += problems.length;
}
if (failures) process.exitCode = 1;
