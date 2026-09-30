# The required stack

Loaded per slice by `prepass-react-modernizer` (Step 2). Apply each section when touching
the corresponding concern.

## Component library: @prepass/ui (consume only)

- Install from the `@prepass` scope; import via named imports only (the library exports no
  defaults).
- The library is built on **Radix UI** primitives, variants via
  **class-variance-authority (cva)**, and conditional classes via the **`cn()`** helper
  (`clsx` + `tailwind-merge`). When you compose library components in the app, follow the
  same patterns so app-level code reads consistently with the library.
- Component taxonomy follows Atomic Design (atoms -> molecules -> organisms -> templates).
  Prefer the highest-level library component that fits before composing lower-level ones.
- **Never** modify, fork, or reach into library internals. If a needed component is missing
  or a prop is inadequate, stop and recommend a library contribution (separate workflow) -
  do not work around it by re-implementing the component in the app.
- Replacement rule: a bespoke component is replaced only when a library component covers
  its purpose and states. Partial matches get composed from library primitives; genuinely
  app-specific UI stays bespoke but must still meet the styling and test-ID rules.

## Styling: Tailwind

- Tailwind is the styling base. The app extends the shared `@prepass/ui` Tailwind preset;
  do not redefine tokens the preset already provides.
- Use the `cn()` utility for conditional and merged class names. No inline style objects
  for anything the design tokens cover. No CSS-in-JS.
- Remove dead bespoke CSS as components are replaced; don't leave orphaned stylesheets.

## State: MobX

- MobX 6 with `makeAutoObservable` in store classes. No decorators.
- React bindings via `mobx-react-lite`: wrap components that read observable state in
  `observer`. Access stores through a React context provider + hook (`useStore`), not
  global singletons imported directly into components.
- Keep stores domain-scoped. Derive with computed getters rather than duplicating state.
  Mutations happen in actions, never inline in components.
- Migration: convert local `useState`/`useReducer` that represents shared or cross-component
  domain state into stores. Leave genuinely local, ephemeral UI state (open/closed, hover)
  as component state - not everything belongs in MobX.

## Validation: Zod

- Validate at every external boundary: form input, API responses, and route params/search.
- `z.infer` is the source of truth for types at those boundaries; replace hand-written
  interfaces that duplicate a schema.
- Parse responses at the fetch layer so the rest of the app works with trusted, typed data.
  Use `safeParse` where a validation failure is an expected, handled outcome (forms);
  `parse` where failure is a programmer error.

## Routing: TanStack Router

- TanStack Router is the default. Use its native Zod integration to type route params and
  search params (`validateSearch` with a Zod schema).
- Prefer the file-based / typed route tree so navigation is type-checked end to end.
- **Exception:** if Phase 0 finds the app already on React Router with meaningful
  investment, do not force a router migration as part of a component retrofit. Flag it as a
  separate, scoped effort and proceed with the existing router, still applying Zod to
  params via a thin validation layer.

## Static test IDs (match the detected convention)

- Every interactive or test-relevant element gets a stable, static identifier using the
  convention detected in Phase 0.
- IDs must be **static and deterministic** - never derived from array index, random values,
  or runtime data that shifts between renders. For list rows, derive from a stable domain
  key (e.g. a record id), not position.
- Scheme (when no existing convention dictates otherwise): `domain-component-element`,
  lowercase, hyphen-delimited, e.g. `invoice-table-row`, `login-form-submit`.
- **Documented default attribute** when the repo has none: `data-testid`.
- Apply IDs to library components via their documented prop for passthrough; don't wrap a
  library component just to attach an ID if it already forwards one.
