# 📚 API Reference

Guide pages come first in this documentation. This page is the grouped API
reference index.

## 🚪 Public Entry Points

### `pyThermoDB`

::: pyThermoDB

### `pyThermoDB.app`

::: pyThermoDB.app

## 👤 Main User Class

### `ThermoDB`

::: pyThermoDB.docs.thermo

### `TableReference`

::: pyThermoDB.docs.tableref

## 🧱 Core Table Objects

### `TableData`

::: pyThermoDB.core.tabledata

### `TableEquation`

::: pyThermoDB.core.tableequation

### `TableMatrixData`

::: pyThermoDB.core.tablematrixdata

### `TableMatrixEquation`

::: pyThermoDB.core.tablematrixequation

### `TableConstants`

::: pyThermoDB.core.tableconstants

## 🏗️ Build and Load Infrastructure

### `CompBuilder`

::: pyThermoDB.builder.compbuilder

### `ManageData`

::: pyThermoDB.manager.managedata

### `CustomRef`

::: pyThermoDB.loader.customref

### `manager.main` (equation body parsers)

::: pyThermoDB.manager.main

## 🔄 Transformers

### `TransData`

::: pyThermoDB.transformer.transdata

### `TransMatrixData`

::: pyThermoDB.transformer.transmatrixdata

## 🧩 References Subsystem

### `ReferenceChecker`

::: pyThermoDB.references.checker

### `Reference Mappers`

::: pyThermoDB.references.reference_mapper

### `ThermoReference`

::: pyThermoDB.references.reference

### `ThermoDatabook`

::: pyThermoDB.references.databook

## Interaction-data tables

`TableInteractionData` stores scalar parameters for an ordered multi-component `Mixture`; it is not a matrix or tensor. Define it with `INTERACTION-SYMBOL`, a `Mixture` column, aligned `STRUCTURE` fields, and row values such as:

```yaml
INTERACTION-SYMBOL: [psi, zeta]
STRUCTURE:
  COLUMNS: [No., Mixture, psi, zeta]
  SYMBOL: [None, None, psi, zeta]
  UNIT: [None, None, 1, 1]
VALUES:
  - [1, "Na{+}|K{+}|Cl{-}", -0.0018, 0.25]
```

Use `data.get("psi", "Na{+}|K{+}|Cl{-}")`. `null` remains unavailable (`None`); numeric zero remains an explicit value. Component order is preserved.