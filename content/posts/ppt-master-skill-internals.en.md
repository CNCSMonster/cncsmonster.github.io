+++
title = "PPT Master Skill Deep Dive: SVG Intermediary, Web Annotations, and Native Editable PPTX"
date = 2026-08-30T00:00:00+08:00
slug = "ppt-master-skill-internals-en"
[taxonomies]
    tags = ["AI Skill", "PPT Master", "DrawingML", "SVG", "AI Agent", "Tooling Research"]
+++

Most AI slide generation tools simply paste full-bleed flat images onto slides. While visually appealing initially, **text cannot be edited, shapes cannot be moved, and zooming in results in blurry rasterization**.

`ppt-master` is an open-source Skill designed for AI Coding Agents (such as Claude Code, Qwen Code, and Codex). Its core value lies in **parsing your documents to produce fully native DrawingML PPTX files where every text box can be edited and every vector shape can be recolored and adjusted.**

---

## 1. End-to-End User Experience

The typical collaboration workflow with this Skill is seamless:

1. **Triggering the Skill**:
   - **Explicit Command**: Trigger directly via slash commands (e.g. `/ppt-master <doc-path>`) or variable injection (`$ppt-master`);
   - **Natural Language Intent**: Say naturally: *"Convert this technical spec into a 10-slide presentation."*
2. **Automated Structuring & Vector Layout**: The AI agent extracts document hierarchy, designs visual outlines, and generates SVG vector code for each slide.
3. **Local Web Preview, In-Place Annotations & Precise Refinement**:
   - A local Flask server runs at `http://127.0.0.1:5050` rendering the generated SVGs;
   - You can review slides in the browser, **click on any unsatisfying text or shape to add an annotation**, and hit **Submit Annotations** to write changes to disk;
   - Return to your terminal and instruct the AI: *"Annotations submitted, please refine."* The AI inspects disk annotations via `check_annotations.py` and regenerates only targeted elements.
4. **Export Native PPTX**: Once satisfied, the final SVGs are compiled locally into a native `.pptx` file ready for secondary editing in Microsoft Office or WPS.

### Ecosystem Comparison

| Skill | Ecosystem & Characteristics | Best Use Case |
| :--- | :--- | :--- |
| `anthropics/skills@pptx` | Official lightweight script for basic shapes & text | Quick, simple presentation outlines |
| **`hugohe3/ppt-master`** | Community comprehensive toolkit with SVG interactive annotations & deep DrawingML output | High-quality, complex technical and business decks |
| `claude-office-skills/skills@ppt-visual` | Community visual-first layout generator | Poster-style and graphic-heavy slides |

---

## 2. Architecture: Why Are Slides Truly Editable?

### The Two-Stage Conversion Architecture (SVG → DrawingML)

PowerPoint relies on Microsoft's **DrawingML** XML specification. Direct generation of DrawingML by LLMs frequently suffers from XML syntax errors and broken files.

`ppt-master` resolves this through a two-stage intermediary model:

```
Source Document → [AI Vector Layout] → SVG Code → [Deterministic Python Script] → DrawingML (PPTX)
```

- **Stage 1 (AI Creative Layout)**: LLMs naturally excel at producing clean SVG markup, handling visual layout, palettes, and typography;
- **Stage 2 (Deterministic Compilation)**: A local Python script (`svg_to_pptx.py`) maps SVG tags (`<text>`, `<rect>`, `<path>`) directly into native PowerPoint DrawingML XML nodes.

---

## 3. Security Audit & Zero-API Fallback

### 1. Security Audit Findings
- **Network Isolation**: Local preview binds strictly to `127.0.0.1:5050` with zero telemetry;
- **Execution Safety**: Zero `eval()` or `exec()` usage; `subprocess` calls only internal deterministic toolchains;
- **File System**: Reads and writes are scoped to project paths with path-traversal safeguards;
- **Verdict**: **Clean and safe.**

### 2. Zero External API Dependency & Offline Manual Mode

The core generation pipeline runs **completely offline without commercial APIs**:

| Pipeline Stage | External API Required? | Execution Mechanism |
| :--- | :--- | :--- |
| **Document Conversion** | ❌ No | Local Python libraries (PyMuPDF, docx, etc.) |
| **SVG Generation & PPTX Export** | ❌ No | Local agent SVG generation + `python-pptx` |
| **Browser Preview & Annotations** | ❌ No | Local Flask (`127.0.0.1:5050`) + `check_annotations.py` |
| **AI Image Gen / Image Search / TTS** | ⚠️ Optional | Configurable across 14+ backends |

**Offline Manual Fallback**:
If no image generation API key is configured, image slots are automatically tagged as `Needs-Manual` with dashed prompt placeholders, ensuring the PPTX export pipeline finishes without blockers.

---

## 4. Installation & Dependency Decoupling

1. **Handling `npx skills add` Timeouts**:
   - The repository contains ~99MB of template assets. If the CLI times out, use `rsync` to backfill `scripts/` (105 Python scripts) from a full clone.
2. **Bypassing PEP 668 via `uv venv`**:
   - Modern Linux distros block global `pip` installation. Use `uv` to establish a clean, isolated virtual environment:
     ```bash
     uv venv ~/.ppt-master/venv
     uv pip install -r requirements.txt --python ~/.ppt-master/venv/bin/python
     ```
3. **Decoupling `pycairo` / `svglib`**:
   - `svglib` (requiring system `libcairo2-dev`) is merely an optional fallback for legacy Office rasterization. Core DrawingML export does not require it and runs smoothly with the remaining 88 dependencies.
