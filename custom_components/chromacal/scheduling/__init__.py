"""ChromaCal's scheduling brain — pure Python, no Home Assistant imports.

Ported from the scheduling logic in dist/chromacal.html (v1). Every function
here takes explicit parameters and returns an explicit value — no module-level
mutable state equivalent to v1's global CFG/_floatCache. See CLAUDE.md's
"Known failure pattern" note: v1 broke twice from a block-scoped variable
being read from a sibling scope after it closed. Explicit params/returns
instead of shared state is how this port avoids that category of bug.
"""
