# Changelog

## Unreleased

### Added

- Package-based project structure under `tacxir/`
- Compatibility wrapper at `tacxIR.py`
- CLI debug modes for token and AST dumps
- Regression tests for the interpreter and CLI surface
- Formal repository documentation and structure notes

### Changed

- The monolithic interpreter was split into focused modules
- The repo now has a documented layout and contribution workflow

### Fixed

- Tokenization, scope handling, short-circuit logic, array mutation, escaped strings, and CLI behavior were hardened during the refactor
