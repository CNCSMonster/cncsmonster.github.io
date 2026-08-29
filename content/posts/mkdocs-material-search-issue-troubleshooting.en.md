+++
title = "Troubleshooting MkDocs (Material Theme) Search: Why Do New Files and English Words Get Missed?"
date = 2026-08-08T00:00:00+08:00
slug = "mkdocs-material-search-issue-troubleshooting-en"
[taxonomies]
    tags = ["MkDocs", "MkDocs Material", "Knowledge Base", "Search Engine", "Lunr.js", "Pagefind", "Troubleshooting"]
+++

When using **MkDocs + Material theme** for personal knowledge bases or documentation sites, you may encounter two counter-intuitive search failure behaviors:

1. **Newly created notes are completely invisible in the search bar**, even though the webpage renders fine (HTTP 200);
2. **A note clearly contains `Handy` in its title and content, but searching for the full word `handy` yields zero results, while typing only `hand` finds it immediately**.

These issues combined often lead authors to believe their notes were lost or misremembered. Based on source code and lifecycle analysis, this post breaks down the root causes of both defects and offers immediate mitigation strategies and modern tooling alternatives.

---

## Core Qualification: The Dual-Layer Defect Overlay

These behaviors do not stem from a single component, but from two independent defects across **MkDocs Core** and the **Material Theme**:

| Issue | Responsible Party | Defect Layer | Underlying Mechanism |
| :--- | :--- | :--- | :--- |
| **New files not indexed** | **MkDocs Core** | Backend build pipeline & Dev Server lifecycle | Incremental reload only tracks modifications of existing files; new file creation does not trigger memory index recalculation |
| **`handy` cannot be found** | **Material Theme** | Frontend query preprocessing & Typeahead implementation | Injected wildcard `*` to simulate instant search, breaking Lunr.js stemming pipeline |

---

## Issue 1: New Files Not Found (MkDocs Core Lifecycle Defect)

### Symptom & Empirical Verification
While `mkdocs serve` is running, adding a new Markdown note allows browsing the page, but the top search bar returns nothing.
- **Test A**: Modifying an **existing** file $\to$ search index updates immediately;
- **Test B**: Creating a **new** file $\to$ search index stays stale until an existing file modification triggers a full rebuild.

### Root Cause
MkDocs is a pure Static Site Generator (SSG). Its local dev server follows a one-way batch processing model. To keep simplicity, it does not maintain a fine-grained incremental state machine in memory. Adding a file only triggers single-page rendering without re-running search index compilation.

### Workaround
During local development, `touch` any existing file to trigger a full rebuild, or restart the dev server.

---

## Issue 2: Searching `handy` Fails, But Searching `hand` Succeeds (Material Theme Query Defect)

### Symptom
A note explicitly contains `Handy`. Searching for `handy` returns no matches, but typing `hand` matches immediately.

### Root Cause: Pipeline Mismatch Between Indexing and Querying
This is a classic defect caused by an **asymmetric processing pipeline** between indexing and searching:

1. **Indexing Pipeline (Exported by MkDocs Core)**:
   English words pass through the Porter Stemmer. For `Handy`, following the rule "consonant + y becomes i", the root stored in the index is `handi`.
2. **Query Pipeline (Controlled by Material Theme)**:
   To implement Typeahead (instant search as you type), Material theme's frontend JS forcibly appends a trailing wildcard `term*` to every query term. However, Lunr.js explicitly specifies: **any term containing `*` bypasses the stemmer pipeline entirely**.
3. **The Mismatch Conflict**:
   - Query `handy` $\to$ Converted to `handy*` (bypasses stemmer) $\to$ Searches index for terms starting with `handy` $\to$ Index only has `handi` $\to$ **Match Failed ❌**
   - Query `hand` $\to$ Converted to `hand*` (bypasses stemmer) $\to$ Searches index for terms starting with `hand` $\to$ Successfully prefix-matches `handi` $\to$ **Match Succeeded ✅**

All English words ending with a consonant plus `y` (such as `study`, `happy`, `handy`) suffer from this bug under Material's default search.

---

## Trade-offs and Architecture Reflection

### 1. Can Switching to Another MkDocs Theme Solve This?
- **What it solves**: Basic built-in themes (`mkdocs`, `readthedocs`) do not inject wildcard hacks, so stemming works properly.
- **The cost**: Loses Material's polished UI, non-blocking Web Worker indexing, and keyboard shortcuts. Furthermore, the "new files not indexed" issue is built into MkDocs core and remains unresolved.

### 2. Can We Integrate Modern Search via Plugins (e.g. `mkdocs-pagefind`)?
- **For Production Builds (`mkdocs build`)**: Highly effective. Pagefind provides symmetric multilingual tokenization and paragraph-level indexing.
- **For Local Development (`mkdocs serve`)**: Broken experience. Pagefind is a post-build indexer that relies on static HTML on disk, conflicting with `serve`'s memory-only rendering model.

---

## Best Practices and Recommendations

### 1. Immediate Mitigation for MkDocs Users
- **Disable English Stemming**: Disable the English stemmer pipeline in `mkdocs.yml` search plugin configuration. Trading off morphological expansion is better than missing exact word queries;
- **Be Mindful of Incremental Boundaries**: Restart `serve` or touch an existing file whenever adding new files.

### 2. Modern Architectural Alternatives
While MkDocs and Material are maintained actively, their foundation remains tied to Python synchronous batch processing and the legacy Lunr.js engine. For new knowledge bases or doc sites, modern alternatives offer superior guarantees:

- **Adopt Modern Static Search Engines (like Pagefind)**: Written in Rust with symmetric multilingual indexing. Modern frameworks (such as **Astro Starlight** out-of-the-box, or **VitePress** via plugins) adopt this natively;
- **Modern Bundlers with Fine-Grained HMR**: Vite/Turbopack-based setups instantly reflect file creations and removals without dev server state inconsistencies.
