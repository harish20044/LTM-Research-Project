backends/
├── base.py                  ← shared SolverResult dataclass + interface (owned jointly)
├── registry.py               ← {"z3": z3.solver.run, "prolog": prolog.solver.run, "asp": asp.solver.run}
│
├── z3/
│   ├── solver.py             ← run(code, timeout) -> SolverResult
│   ├── parser.py             ← extracts the answer variable's value from Z3's model output
│   ├── syntax_reference.md   ← short cheat-sheet fed into the autoformalizer prompt
│   ├── examples/             ← 3-5 worked NL-passage → Z3-code pairs, for few-shot prompting
│   └── tests/
│       └── test_solver.py    ← hand-written constraints with known answers, sanity-checks solver.py itself
│
├── prolog/
│   ├── solver.py             ← shells out to `swipl`, captures stdout, enforces timeout
│   ├── parser.py
│   ├── syntax_reference.md
│   ├── examples/
│   └── tests/
│
└── asp/
    ├── solver.py             ← shells out to `clingo`, captures stable-model output
    ├── parser.py
    ├── syntax_reference.md
    ├── examples/
    └── tests/


What each file actually does

solver.py — the only piece that touches the actual engine. For Z3 this is Python bindings running in-process (still worth a hard timeout via signal or a subprocess wrapper, since a malformed constraint can hang); for Prolog and ASP it's subprocess.run(["swipl", ...], timeout=...) / subprocess.run(["clingo", ...], timeout=...), since those are external binaries, not Python libraries. This is also where you catch and classify failures: syntax error vs. unsat/no solution vs. timeout vs. success — these need to be distinguishable, because your ablation study reports on them separately (fallback rate, executable rate).

parser.py — solvers output messy raw text (Z3's model dump, Prolog's X = 19000.0, Clingo's stable-model listing). This extracts just the answer value in a clean, comparable format before it goes to the verbalizer.

syntax_reference.md — a short, fixed cheat-sheet of that backend's syntax, included in the autoformalizer's prompt. This directly matters for ASP specifically: the "LLMs as ASP Programmers" paper found ASP underperforms zero-shot mainly because it's less represented in LLM training data than Z3's Python API — giving the autoformalizer a compact reference closes most of that gap. Keep this file the same length/style across all three backends so you're not accidentally giving one backend better scaffolding than another (a confound we flagged earlier).

examples/ — a handful of hand-verified natural-language-passage → correct-code pairs, used as few-shot examples in the autoformalizer prompt. These should be held out from your actual evaluation set — don't use real IndiaFinBench items here, or you'd be leaking test data into your prompts.

tests/ — unit tests that check solver.py itself works correctly, independent of any LLM involvement: feed it a hand-written, known-correct formal program, confirm it returns the right SolverResult. This is also exactly the infrastructure you'd reuse for Option A's optional A6 oracle condition (hand-coded formalizations, no LLM autoformalization step) — the oracle run just calls solver.py directly with your own code instead of LLM-generated code.