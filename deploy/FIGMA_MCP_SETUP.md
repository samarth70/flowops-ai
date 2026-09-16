# 🎨 Figma & UI Design MCP Server Integration Guide

This guide explains how to connect a **Figma Model Context Protocol (MCP)** server to your IDE/agent environment so your AI pair programmer can directly inspect design tokens, Figma frames, component variables, and layouts from design platforms like **Refero.design**, **Mobbin**, and **Figma**.

---

## 1. What the Figma MCP Server Does
* **Direct Token & Frame Extraction**: The AI reads exact CSS spacing, hex colors, border-radii, and layout hierarchies directly from Figma files.
* **Component Architecture Mapping**: Converts Figma frames into clean, responsive React + Vanilla CSS components.
* **Design Consistency Auditing**: Automatically identifies contrast issues, padding discrepancies, and unstyled ad-hoc classes.

---

## 2. Quick Setup (3 Minutes)

### Step A: Generate a Figma Personal Access Token
1. Open your [Figma Settings](https://www.figma.com/settings).
2. Scroll to **Personal access tokens**.
3. Click **Generate new token**, give it a name (e.g. `Antigravity IDE`), and copy the token (`figd_...`).

### Step B: Configure the MCP Server
Add the Figma MCP server to your MCP configuration file (e.g. `mcp_config.json`):

```json
{
  "mcpServers": {
    "figma": {
      "command": "npx",
      "args": [
        "-y",
        "@figma/mcp-server"
      ],
      "env": {
        "FIGMA_ACCESS_TOKEN": "your_figma_personal_access_token_here"
      }
    }
  }
}
```

---

## 3. Top Free UI/UX Inspiration Resources for Modern B2B & AI Apps

| Resource | Specialty | What to Look For |
| :--- | :--- | :--- |
| **[Refero.design](https://refero.design)** | Curated real-world SaaS and AI product flows | Attio CRM deal views, Linear issue boards, Ramp finance drawers. |
| **[Mobbin.com](https://mobbin.com)** | Mobile and Web application design patterns | Multi-step onboarding, modal interactions, data tables. |
| **[Raycast.com](https://raycast.com)** | High-density keyboard-first UX | Floating command palettes (`Cmd+K`), monospace status chips. |
| **[Attio.com](https://attio.com)** | Next-generation modern CRM | Pill-based metadata filters, ARR tally banners, contact avatars. |
