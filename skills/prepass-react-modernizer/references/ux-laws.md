# PrePass UX Laws

Loaded by `prepass-react-modernizer` (Step 2) **only when a UX-affecting decision arises**.
These are not styling rules - they guide layout, interaction, and information decisions you
make while retrofitting. When a UX tradeoff is non-obvious, name the relevant law in your
reasoning so the decision is reviewable.

- **Jakob's Law:** prefer conventional, familiar patterns over novel ones. A retrofit
  should make the app behave more like what users already expect, not less.
- **Hick's Law / Choice overload:** when consolidating UI, reduce the number of competing
  choices presented at once. Group and prioritize.
- **Fitts's Law:** keep primary actions large and close to where interaction happens;
  preserve or improve touch target sizes when swapping components.
- **Miller's Law / Chunking:** break dense content into scannable, labeled groups
  (headings, lists, boxed regions) rather than walls of fields or text.
- **Law of Proximity / Common Region:** related controls stay visually grouped; use the
  library's card/section primitives to make grouping explicit.
- **Postel's Law:** be liberal in what inputs you accept and forgiving in forms; clean and
  normalize user input rather than rejecting imprecise entry. Pair this with Zod for
  trustworthy parsing.
- **Aesthetic-Usability Effect:** consistent, polished library components raise perceived
  usability - a reason to prefer `@prepass/ui` over bespoke even at parity.
- **Tesler's Law:** some complexity is irreducible; when you can't remove it, absorb it
  into the system (smart defaults, validation, derived state) rather than pushing it onto
  the user.
