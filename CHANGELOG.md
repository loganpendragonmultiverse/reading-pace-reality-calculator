# Changelog

## 1.1.3 - 2026-10-18

- Calculate session ceilings from exact finite ratios so a completed session boundary does not add an extra session or break.
- Round scenario elapsed time from the exact reading time and intervening breaks.
- Return exit status 2 for failed stdout writes, including a closed pipe.

## 1.1.2 - 2026-10-18

- Create report files exclusively so a destination arriving during export is preserved.
- Return an actionable input error when finite values exceed the decimal calculation range, before creating a report.

## 1.1.1 - 2026-10-16

- Correct the completed 1.1.0 release wording and dates; feature behavior is unchanged.

## 1.1.0 - 2026-10-15

- Added optional named session/break scenarios and validation of finite, non-negative numeric inputs while preserving default report fields.

## 1.0.0 - 2026-07-26

- Released the first complete Reading Pace Reality Calculator command-line workflow.
- Added deterministic reporting, representative examples, cross-platform tests, and explicit limitations.
