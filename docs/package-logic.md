# 🧠 Package Logic

This page documents how major package subsystems work together:

- `core`
- `builder`
- `loader`
- `manager`
- `references`
- `transformer`
- app-level entry points (`pyThermoDB.app`, `pyThermoDB.thermodb`)

## 🧭 Runtime Flow

Typical flow for a single-component workflow:

1. `pyThermoDB.init(...)` creates a `ThermoDB` object.
2. `ThermoDB` inherits `ManageData`, which loads built-in references and merges custom references.
3. `ThermoDB.build_data(...)` / `build_equation(...)` retrieves raw table records.
4. `transformer` normalizes payloads into symbol/value/unit structures.
5. `core` classes (`TableData`, `TableEquation`, etc.) expose retrieval and calculation APIs.
6. `CompBuilder` collects these objects and saves/loads a portable `.pkl` thermodb.

## 🧱 `core`: Runtime Property Objects

Primary classes exported by `pyThermoDB.core`:

- `TableData`: scalar property tables (`get_property`, structure access)
- `TableEquation`: executable equation tables (`cal`, args/parms/returns)
- `TableMatrixData`: matrix/binary-mixture data retrieval (`ij`, `mat`, matrix property access)
- `TableMatrixEquation`: matrix equation objects
- `TableConstants`: table-wide constants (`get_constant`)

`core` objects are the final user-facing runtime entities created from references/tables.

## 🏗️ `builder`: ThermoDB Assembly

`CompBuilder` is the composition container:

- accepts any supported core object via `add_data(...)`
- stores a mixed property/function/constants bundle
- persists bundle with metadata (`build_version`, timestamp, python version)
- loads back the same structure through `load_thermodb(...)`

Use `pyThermoDB.build_thermodb(...)` for creation and `pyThermoDB.load_thermodb(...)` for reuse.

## 🧩 `loader`: Custom Reference Ingestion

`CustomRef` handles external reference inputs:

- accepts YAML/Markdown reference sources (`reference`, legacy `yml`/`md`)
- accepts external table CSV paths (`tables` / legacy `csv`)
- supports two modes:
  - `NORMAL`: reference + external table files
  - `VALUES`: inline/table-values style content in reference source
- validates paths and parses raw content into merged `REFERENCES` structure

This is the main ingress for project-specific thermodynamic datasets.

## 🗃️ `manager`: Reference/Metadata Backbone

`ManageData` centralizes:

- loading built-in `config/reference.yml`
- merging custom references from `CustomRef`
- databook and table discovery/indexing
- table metadata extraction (types, structure, descriptions)
- symbol loading and normalization

`ThermoDB` (docs/thermo class) builds on this backbone to provide high-level user operations.

`manager.main` additionally provides equation-body parsing utilities used by build/transform flows.

## 📚 `references`: Authoring, Validation, and Mapping

Key responsibilities:

- reference modeling (`ThermoDatabook`, `ThermoReference`)
- reference validation and availability checks (`ReferenceChecker`)
- symbol governance (`SymbolController`)
- mapping reference content into build configs/rules:
  - `component_reference_mapper`
  - `mixture_reference_mapper`
  - `constants_reference_mapper`

These modules power higher-level builders in `pyThermoDB.thermodb`, especially
`check_and_build_*` and `*_from_reference` APIs.

## 🔄 `transformer`: Payload Normalization

- `TransData`: converts row payloads into normalized dict keyed by columns/symbols.
- `TransMatrixData`: converts matrix/mixture payloads and writes multiple component keys
  (name, formula, and state-qualified forms).

Transformers isolate API/table payload shape from final `core` object behavior.

## 🏁 App vs High-Level Build APIs

- `pyThermoDB.app`: operational workflow APIs (`init`, `ref`, `build_thermodb`, `load_thermodb`).
- `pyThermoDB.thermodb`: orchestration APIs for config-driven build pipelines
  (single component, components set, mixtures, constants, reference-driven build).

Use `app` APIs for interactive/local operations, and `thermodb` APIs for repeatable, config-first pipelines.

## ⚠️ Important Design Notes

!!! warning "Table type controls behavior"
    Always inspect table type first (`Data`, `Equation`, `Matrix-Data`,
    `Matrix-Equation`, `Constants`) because build and retrieval paths diverge.

!!! warning "Component key semantics matter"
    Mixed APIs use `Name`, `Formula`, `Name-State`, and `Formula-State`.
    Inconsistent key choice is a common cause of availability/build failures.

!!! warning "Custom reference mode"
    If only reference content is provided, `CustomRef` can enter `VALUES` mode.
    If external CSV tables are expected, ensure `tables` paths are provided for `NORMAL` mode.
