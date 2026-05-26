# 🎨 Mini-C Compiler Visualizer Frontend (React + Vite)

This is the interactive frontend for the **Mini-C Compiler Front-End Visualizer**. It is built using **React**, **Vite**, **D3.js**, and vanilla CSS.

## Features implemented here:
- **Workspace Split Resizer**: Interactive draggable divider bar to adjust code editor and results panel width according to developer demands.
- **Interactive Parse Tree**: Rendered dynamically using D3.js, supporting node collapse/expand, fluid panning, and zoom controls.
- **Diagnostics Console**: Display panels for compiled Token Stream, active Scope-aware Symbol Table, and full Lexical/Syntax/Semantic Compiler errors and warnings.

## Development Setup

To run the frontend locally:

```bash
# Install NPM dependencies
npm install

# Run the local development server (typically launches on http://localhost:5173)
npm run dev
```

> [!NOTE]
> Make sure the Python Flask backend is running on `http://localhost:5000` to handle compilation and semantic analysis requests.

For full architectural diagrams, grammar specifications, and backend details, please refer to the [Root README](../README.md).
