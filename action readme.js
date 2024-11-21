const fs = require("fs");
const path = require("path");
const yaml = require("js-yaml");

// Define directories
const ACTION_DIR = path.join(__dirname, ".");
const README_FILE = path.join(__dirname, "README.md");

// Initialize README content
let readmeContent = `# Reusable GitHub Actions

This repository contains reusable GitHub Actions designed to automate common tasks and promote consistency across projects.

## Table of Contents
1. [Overview](#overview)
2. [Available Actions](#available-actions)
3. [Inputs](#inputs)
4. [Outputs](#outputs)
5. [Usage Examples](#usage-examples)
6. [License](#license)

---

## Overview

Reusable GitHub Actions enable you to:
- Standardize processes like builds, tests, and deployments.
- Reduce duplication by centralizing commonly used workflows.
- Simplify GitHub Actions configuration in your projects.

---

## Available Actions
`;

/**
 * Parse a YAML file and return its content.
 * @param {string} filePath Path to the YAML file
 * @returns {object} Parsed YAML content
 */
const parseYamlFile = (filePath) => {
  try {
    const fileContent = fs.readFileSync(filePath, "utf8");
    return yaml.load(fileContent);
  } catch (error) {
    console.error(`Error parsing YAML file: ${filePath}`, error);
    return null;
  }
};

/**
 * Generate a table from the `inputs` section of an action's metadata.
 * @param {object} inputs The inputs object from action.yml
 * @returns {string} Markdown table for inputs
 */
const generateInputsTable = (inputs) => {
  if (!inputs) return "No inputs defined.\n";

  let table = "| **Input** | **Description** | **Required** | **Default** |\n";
  table += "|-----------|----------------|--------------|-------------|\n";

  for (const [key, value] of Object.entries(inputs)) {
    const description = value.description || "No description";
    const required = value.required ? "Yes" : "No";
    const defaultValue = value.default || "N/A";
    table += `| \`${key}\` | ${description} | ${required} | ${defaultValue} |\n`;
  }

  return table;
};

/**
 * Generate a table from the `outputs` section of an action's metadata.
 * @param {object} outputs The outputs object from action.yml
 * @returns {string} Markdown table for outputs
 */
const generateOutputsTable = (outputs) => {
  if (!outputs) return "No outputs defined.\n";

  let table = "| **Output** | **Description** |\n";
  table += "|------------|-----------------|\n";

  for (const [key, value] of Object.entries(outputs)) {
    const description = value.description || "No description";
    table += `| \`${key}\` | ${description} |\n`;
  }

  return table;
};

/**
 * Generate usage example for the action.
 * @param {string} name Action name
 * @returns {string} Markdown example
 */
const generateUsageExample = (name) => `
\`\`\`yaml
- name: ${name}
  uses: <OWNER>/<REPO>@<VERSION>
  with:
    input-key: input-value
\`\`\`
`;

// Scan for actions (action.yml or action.yaml files)
const actionFiles = fs.readdirSync(ACTION_DIR).filter((file) =>
  file.match(/^action\.ya?ml$/)
);

// Add metadata for each action to the README
actionFiles.forEach((actionFile) => {
  const actionPath = path.join(ACTION_DIR, actionFile);
  const actionContent = parseYamlFile(actionPath);

  if (actionContent) {
    const actionName = actionContent.name || "Unnamed Action";
    const description = actionContent.description || "No description provided.";

    readmeContent += `\n### **${actionName}**\n`;
    readmeContent += `${description}\n\n`;

    readmeContent += "#### Inputs\n";
    readmeContent += generateInputsTable(actionContent.inputs) + "\n";

    readmeContent += "#### Outputs\n";
    readme
