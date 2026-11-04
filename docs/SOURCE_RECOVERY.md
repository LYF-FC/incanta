# Source recovery audit — 2026-11-04

## Chosen baseline

`~/Documents/Projects/Incanta` is the most recently edited substantive source tree found in this audit. Its main source edits are dated 2025-10-06, through approximately 23:59 local filesystem time. Its Flask application, plain JavaScript frontend and memory/gauge modules form the baseline imported into this repository.

The original folder remains unchanged. Only 16 explicitly selected source/dependency/launcher files were copied; two trailing spaces in the gauge engine were subsequently removed. Private personality files, chat histories, model weights, generated media, the environment and the old environment example were not imported. A new synthetic personality example was authored separately. Requirements are preserved unchanged.

File dates support the choice but do not establish a complete version history. File hashes and source structure were also compared. Python syntax was checked without executing the application. Neither this baseline nor any older variant has been proven operational by this audit.

## Folder assessment

Paths below are relative to `~/Documents/`.

| Location | Observed contents | Recommendation |
| --- | --- | --- |
| `Projects/Incanta` | Latest substantial source; local model, environment and private runtime/configuration assets | Keep as the untouched original recovery source. Use this Git checkout for future source changes. |
| `IncantaOLD` | Distinct earlier implementation, edited earlier on 2025-10-06; Streamlit app, alternative state/memory code, expression-image selection, static frontend assets | Retain as a legacy reference. It contains unique source and assets absent from the chosen baseline. |
| `Incanta_OLD` | Two small Python modules from September 2025 | Redundant source: both files exactly match entries in `Incanta_Full_Project.zip`. Optional cleanup candidate once that backup is verified. |
| `incanta_immersive_template` | Finder metadata only | Unnecessary for development; optional cleanup candidate. Its similarly named ZIP is a separate, nonempty artifact. |
| `incanta_project_evolve` | Eight zero-byte source/template placeholders, plus Finder metadata | Unnecessary for development; optional cleanup candidate. |
| `incanta_save_load_expressions` | Finder metadata only | Unnecessary for development; optional cleanup candidate. Its similarly named ZIP contains actual older code. |

`IncantaOLD` is not a drop-in replacement: static inspection found that its LLM wrapper calls memory and emotion methods absent from its own classes. The newer baseline also has documented issues; see the README. Do not merge the variants indiscriminately.

## Archive assessment

`Incanta 2.zip` is approximately 4.20 GB compressed. Most of its size comes from a bundled GGUF model and Python environment. Its substantive app is an earlier Gradio implementation with session loading/reset and expression-image selection. Those features are useful historical references, but the ZIP is not the latest source baseline.

`20251006 - Incanta.zip` is also approximately 4.20 GB. Comparing ZIP entry names, uncompressed sizes and CRCs (excluding Finder metadata): all entries from `Incanta 2.zip` exist in the dated archive; it has eight additional entries, including two core source modules. One shared private-data entry differs. Consequently the dated archive does not establish that every private version in `Incanta 2.zip` is redundant. Private contents were not printed, imported or committed. These are metadata comparisons, not full byte-for-byte integrity verification of the multi-gigabyte archives.

Additional small ZIPs were inspected for source inventory, including `Incanta_Full_Project.zip`, `Incanta_Final.zip`, `Incanta.zip`, `Incanta_Immersive_Final.zip`, `Incanta_Immersive_Update.zip`, `incanta_backend_fixed.zip`, `incanta_immersive_template.zip`, `incanta_project_evolve.zip`, and `incanta_save_load_expressions.zip`. They are historical templates/variants rather than newer replacements for the selected baseline. Notably, the immersive and save/load ZIPs contain nonempty code even though their corresponding extracted folders are empty.

## Retention

The active source only needs one Git working copy. Retain the untouched latest original, the distinct `IncantaOLD` source, and archives containing unique source or private data until a separately authorized consolidation. Model weights and environments are not source backups; environments can be recreated, while model availability and licensing should be checked before removing the only retained copy.

No originals or archives were deleted, moved or modified. This audit does not authorize cleanup. Future deletion should use a concrete reviewed list and explicit owner approval.
