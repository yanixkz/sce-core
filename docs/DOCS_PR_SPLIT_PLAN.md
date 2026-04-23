# Docs PR Split Plan

This document replaces the broad documentation PR with three focused PR tracks for predictable review and safer merges.

## Why split

- Reduce review scope per PR.
- Separate structural changes from content decisions.
- Allow independent accept/revert by goal.

## PR 1 — README structure only

**Goal:** Improve readability and navigation in `README.md` without changing product claims.

### In scope

- Reordering existing sections.
- Renaming headings for clarity.
- Adding/removing separators for better scanability.
- Improving section flow (e.g., quick start earlier, deep details later).

### Out of scope

- New positioning statements.
- New ICP/audience claims.
- New adoption guidance.
- New localization content.

### Done when

- Only structure/order/formatting changes are present.
- No new meaning-bearing product statements are introduced.
- Reviewers can approve this PR without content strategy discussion.

---

## PR 2 — Positioning & adoption content

**Goal:** Add and discuss high-level messaging in a dedicated content PR.

### In scope

- One-line positioning.
- ICP / audience framing.
- Adoption path.
- “When not to use” guidance.

### Out of scope

- Structural reshuffle unrelated to content.
- Localization files.

### Done when

- Content decisions are explicit and reviewed as messaging decisions.
- The PR contains rationale for each new section.
- No unrelated structural churn.

---

## PR 3 — Russian overview

**Goal:** Move `docs/OVERVIEW_RU.md` into a dedicated localization PR and decide whether RU docs should be in the main repository now.

### In scope

- Add/update `docs/OVERVIEW_RU.md`.
- Team decision note: keep in main repo now vs postpone.
- If accepted, add a minimal README link to RU overview.

### Out of scope

- English positioning/content debates.
- Large README restructuring.

### Done when

- Localization changes are isolated.
- Repository policy decision for RU docs is recorded.
- README cross-link (if needed) is minimal and explicit.

---

## Acceptance checklist (cross-PR)

- [ ] At least 2–3 focused PRs exist instead of one broad docs PR.
- [ ] Each PR maps to exactly one objective: structure / content / localization.
- [ ] Each PR description clearly states “what changed” and “why”.
- [ ] No mixing of structural refactoring and new meaning-bearing claims.
- [ ] Review becomes fast and predictable due to reduced scope.

## Definition of done

- [ ] All three tracks are created and reviewed independently.
- [ ] Each track has an agreed change set.
- [ ] The original broad PR is no longer used as the integration unit.
