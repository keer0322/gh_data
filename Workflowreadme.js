const fs = require("fs");
const path = require("path");
const yaml = require("js-yaml");

// Define directories
const WORKFLOW_DIR = path.join(__dirname, ".github/workflows");
const README_FILE = path.join(__dirname, "README.md");

// Initialize README content
let readmeContent = `# Reusable GitHub Actions and Workflows

This repository contains reusable GitHub Actions and workflows designed to streamline and standardize CI/CD processes across multiple projects.

## Table of Contents
1. [Overview](#overview)
2. [Getting Started](#getting-started)
3. [Usage Examples](#usage-examples)
4. [Inputs](#inputs)
5. [Outputs](#outputs)
6. [License](#license)

---

## Overview

Reusable workflows and actions allow you to:
- Centralize and maintain common workflows in one place.
- Simplify GitHub Actions configuration across repositories.
- Promote consistency and reduce duplication of code.

---

## Getting Started

1. Ensure your repository is configured to use GitHub Actions.
2. Define the reusable workflows or actions in your \`.github/workflows\` directory.

---

## Usage Examples

### Using a Reusable Workflow
You can reference reusable workflows in your repository like this:

\`\`\`yaml
name: Example Workflow

on:
  push:
    branches:
      - main

jobs:
  example-job:
    uses: <OWNER>/<REPO>/.github/workflows/<WORKFLOW_FILE>.yaml@<VERSION>
    with:
      input-1: value
      input-2: value
    secrets:
      SECRET_NAME: \${{ secrets.SECRET_NAME }}
\`\`\`

---

## Inputs
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
 * Generate an inputs table from a workflow or action's inputs section.
 * @param {object} content Parsed YAML content
 * @returns {string} Inputs table as a Markdown string
 */
const generateInputsTable = (content) => {
  if (!content || !content.inputs) {
    return "No inputs defined.\n";
  }

  let table = "| **Input** | **Description** | **Required** | **Default** |\n";
  table += "|-----------|----------------|--------------|-------------|\n";

  for (const [inputName, inputData] of Object.entries(content.inputs)) {
    const description = inputData.description || "No description";
    const required = inputData.required ? "Yes" : "No";
    const defaultValue = inputData.default || "N/A";
    table += `| \`${inputName}\` | ${description} | ${required} | ${defaultValue} |\n`;
  }

  return table;
};

// Read workflow files and generate the Inputs section
if (fs.existsSync(WORKFLOW_DIR)) {
  const workflowFiles = fs.readdirSync(WORKFLOW_DIR).filter((file) =>
    file.endsWith(".yaml") || file.endsWith(".yml")
  );

  if (workflowFiles.length > 0) {
    workflowFiles.forEach((workflowFile) => {
      const workflowPath = path.join(WORKFLOW_DIR, workflowFile);
      const workflowContent = parseYamlFile(workflowPath);

      if (workflowContent) {
        readmeContent += `### Workflow: \`${workflowFile}\`\n`;
        readmeContent += generateInputsTable(workflowContent);
        readmeContent += "\n";
      }
    });
  } else {
    readmeContent += "No workflows found in `.github/workflows`.\n";
  }
} else {
  readmeContent += "Workflow directory `.github/workflows` does not exist.\n";
}

// Write the README file
fs.writeFileSync(README_FILE, readmeContent, "utf8");
console.log("README.md generated successfully!");
