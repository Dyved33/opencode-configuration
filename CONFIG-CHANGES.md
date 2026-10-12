# Config changes

Summary of the tooling added to this vault and how to operate it. Everything here is
local; nothing leaves the machine. The notes themselves are unaffected.

## What was added

| # | Feature | What it does |
|---|---|---|
| 1 | **Docling OCR fallback** in `leggi-slide.py` | Reads PDFs/PPTX that have no text layer (scanned pages, slides exported as images) |
| 2 | **Semantic search server** `obsidian-mcp-search` | Searches the notes by meaning, not just exact words; exposed to OpenCode as the `obsidian-search` MCP server |
| 3 | **ACP plugin** `@tuanhung303/opencode-acp` | Compacts the conversation by time, not only by size, for long sessions |
| 4 | **Book reader** `libri.py` + `/libro` command | Reads the textbooks in `libri/` (list, table of contents, page, search) |

## Prerequisites (installed)

System packages (already present on this machine): `poppler-utils` (`pdftotext`),
`tesseract-ocr` + `tesseract-ocr-ita`, LibreOffice (only to convert legacy `.ppt`).

Python packages, installed for the current user (PEP 668-safe):

```bash
python3 -m pip install --user --break-system-packages pypdf "obsidian-mcp-search[server]" docling
```

OpenCode plugins, set in `opencode.json` (`plugin` array): `@tuanhung303/opencode-acp@latest`
(the pre-existing `opencode-parser` plugin is global, in `~/.config/opencode/opencode.jsonc`).

## 1. Docling OCR fallback

`leggi-slide.py` still uses `pdftotext -layout` first. If more than half of the pages come
out empty, it retries with Docling (OCR) automatically. This is transparent: the same
commands keep working.

- Only kicks in for files up to **60 pages** (default), to avoid converting a 2000-page book
  page by page.
- Override the limit: `LEGGI_SLIDE_DOCLING_LIMITE=N`.
- Force OCR on a long file: `LEGGI_SLIDE_DOCLING_FORZA=1 python3 .opencode/scripts/leggi-slide.py FILE 28`.
- First run downloads the OCR models (cached under `~/.local/.../rapidocr`). Docling also
  pulls PyTorch/CUDA wheels at install time; the CUDA warning on a CPU-only machine is harmless.

```bash
python3 .opencode/scripts/leggi-slide.py "slide.pdf" 28      # OCR happens automatically if needed
```

## 2. Semantic search (`obsidian-mcp-search`)

Indexes the Markdown notes under `primo semestre/` and answers queries by embedding
similarity (hybrid lexical + vector). It runs as an HTTP MCP server on
`http://127.0.0.1:8848/mcp`; OpenCode connects to it via the `mcp` block in `opencode.json`.

- Embedding model: `sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2` (384-dim,
  ~50 languages). The tool's own default, `intfloat/multilingual-e5-small`, is **not
  supported** by the installed `fastembed` and must be overridden.
- The registry lives in `~/.config/obsidian-mcp-search/config.toml`; the index in
  `~/.cache/obsidian-mcp-search/`.
- Registered vault: name `appunti` -> `/home/david/appunti_terzo_anno_informatica/primo semestre`.
- Tools exposed: `list_vaults`, `search`, `read_note`, `reindex`.

Register / re-index a vault (note the env var):

```bash
OMCS_EMBED_MODEL="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2" \
  obsidian-mcp-search add-vault appunti "/home/david/appunti_terzo_anno_informatica/primo semestre"
```

### Service

A user systemd unit starts the server automatically:

```bash
systemctl --user status  obsidian-mcp-search
systemctl --user restart obsidian-mcp-search     # reloads and re-indexes
systemctl --user stop    obsidian-mcp-search
journalctl --user -u obsidian-mcp-search -n 50
```

Unit file: `~/.config/systemd/user/obsidian-mcp-search.service`. It sets
`OMCS_EMBED_MODEL`, `OMCS_HOST=127.0.0.1`, `OMCS_PORT=8848`. To keep it running when you are
not logged in: `sudo loginctl enable-linger david`.

### Important: do not use the `search` CLI

`obsidian-mcp-search search --vault <name|path> "query"` ignores `OMCS_EMBED_MODEL` and
builds a throwaway index at `<vault>/.omcs-index.sqlite` — if you pass a vault *name* it
creates a stray `appunti/` folder in the cwd. Use the MCP server (or OpenCode) instead.

## 3. ACP plugin

`@tuanhung303/opencode-acp` keeps long sessions under control by pruning stale context
while preserving active constraints. No configuration needed; just the entry in
`opencode.json`.

## 4. Book reader (`libri.py` / `/libro`)

Textbooks live in `libri/<Course name>.pdf`, one per course. The two present books were
renamed to match their course folders:

- `libri/Introduzione IA.pdf`
- `libri/Introduzione sicurezza.pdf`
- **Still missing:** `Architettura reti e internet`, `Basi di dati e sistemi informativi con laboratorio`, `Programmazione web e mobile con laboratorio`.

Commands (also available as `/libro` inside OpenCode):

```bash
python3 .opencode/scripts/libri.py elenco                       # books + matched course
python3 .opencode/scripts/libri.py info FILE                    # pages, title, course
python3 .opencode/scripts/libri.py indice FILE                  # table of contents (PDF bookmarks)
python3 .opencode/scripts/libri.py pagina FILE 28               # text of a page (or 19-21)
python3 .opencode/scripts/libri.py cerca FILE "firewall"        # pages containing the text
```

`indice` reads the PDF bookmarks; if a book has none (e.g. `Introduzione IA.pdf`) it says so
and you fall back to `pagina` / `cerca`. Books are a complement to the notes, never a default
source: the agent asks for consent before using one (rule 11 of `AGENTS.md`).

## opencode.json

The config declares the `plugin` array (ACP), the `mcp` server, `compaction`, the
`watcher` ignore list, and a `permission` block. The permission block enforces the
restrictions in `AGENTS.md`: `edit` denies everything except `.md` (with explicit denials for
`AGENTS.md`, `.opencode/**`, `esercizi/`, `opencode.json`, `CONFIG-CHANGES.md` and the two
`prompt/` files); `bash` denies everything except an allowlist (the five vault scripts, `ls`,
`grep`, `rg`, `wc`, `pdfinfo`, `pdftotext`, `tesseract`, read-only git); `external_directory`
keeps the agent inside the vault. `pdftoppm` and `dividi-appunti.py --scrivi` ask for
confirmation.

Any change to `opencode.json` or `.opencode/` requires an OpenCode restart.

## Keeping the index fresh

The server watches `primo semestre/` and re-indexes changed notes automatically. If search
results look stale after bulk edits:

```bash
systemctl --user restart obsidian-mcp-search
```

or, from OpenCode, call the MCP tool `reindex` with `vault="appunti"`.

## Troubleshooting

| Symptom | Fix |
|---|---|
| `Model intfloat/multilingual-e5-small is not supported` | Set `OMCS_EMBED_MODEL` to a supported model (see section 2) |
| OpenCode does not see `obsidian-search` | `systemctl --user status obsidian-mcp-search`, then restart OpenCode |
| Server refuses a non-localhost bind | It requires `MCP_AUTH_TOKEN`; keep it on `127.0.0.1` |
| Docling runs on a huge file and hangs | It is skipped above 60 pages; never set `LEGGI_SLIDE_DOCLING_FORZA=1` on a big book |
| Stray `appunti/` folder created | From the CLI `search` bug (section 2); delete it |
