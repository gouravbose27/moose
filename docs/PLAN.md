# Plan: "Moose" — a minimal Python-inspired interpreter (learning project)

## Decisions locked in with user
- Implementation language: Python 3.13 (venv already present at .venv)
- Architecture: tree-walking interpreter (Lexer -> Parser -> AST -> Evaluator), no bytecode VM
- Language name: "moose", file extension `.moose`
- Blocks delimited by explicit `end` keyword (not indentation, not braces) — e.g. `if x < 5: ... else: ... end`
- REPL included, plus file execution
- Feature set v1: variables declared/assigned with `let` (`let x = 5`, every assignment repeats `let`, no bare `x = 5`), arithmetic (+ - * / % and parens, unary -), comparisons (== != < > <= >=), booleans (true/false, and/or/not), if/else, functions (def/return, recursion, closures), `#` comments
- Explicitly excluded from v1 (confirmed with user): strings, lists, while loops — noted as natural v2 extensions
- if/else blocks do NOT introduce a new variable scope (matches real Python behavior); only function calls create a new Environment
- Return uses an internal Python exception (ReturnSignal) to unwind the call stack — standard technique
- Truthiness: booleans used as-is; numbers are truthy if nonzero (fallback since no separate truthy protocol needed)
- Built-in `print(...)` function needed since no strings — prints numbers/booleans to stdout
- Lexing/parsing: use the `lark` library instead of a hand-rolled lexer/parser. Grammar lives in `moose/grammar.lark`, parsed with Lark's `lalr` parser (fast, gives clear `UnexpectedToken`/`UnexpectedCharacters` errors with line/column info). A `lark.Transformer` (`moose/ast_builder.py`) converts the Lark parse tree into the same `moose/ast_nodes.py` dataclasses used by the interpreter, so `environment.py`/`interpreter.py` are unaffected by this choice.

## Grammar sketch (informal, no code)
```
program     -> statement* EOF
statement   -> if_stmt | func_def | return_stmt | assignment | expr_stmt
if_stmt     -> "if" expression ":" NEWLINE statement* ("else" ":" NEWLINE statement*)? "end"
func_def    -> "def" IDENTIFIER "(" (IDENTIFIER ("," IDENTIFIER)*)? ")" ":" NEWLINE statement* "end"
return_stmt -> "return" expression?
assignment  -> "let" IDENTIFIER "=" expression
expr_stmt   -> expression
expression  -> or_expr
or_expr     -> and_expr ("or" and_expr)*
and_expr    -> not_expr ("and" not_expr)*
not_expr    -> "not" not_expr | comparison
comparison  -> term (("=="|"!="|"<"|">"|"<="|">=") term)*
term        -> factor (("+"|"-") factor)*
factor      -> unary (("*"|"/"|"%") unary)*
unary       -> "-" unary | call
call        -> primary ("(" (expression ("," expression)*)? ")")*
primary     -> NUMBER | "true" | "false" | IDENTIFIER | "(" expression ")"
```
Multi-char operators must be lexed greedily before single-char ones: `==` before `=`, `<=`/`>=` before `<`/`>`, `!=` only as a pair (no bare `!`). Lark's standard lexer handles this automatically (string-literal terminals get higher priority than regex terminals, and longer literals win over shorter ones), so no manual ordering code is needed.
NEWLINE is a real terminal ending a statement; consecutive blank/comment-only lines collapse to one NEWLINE via a regex terminal (`/\n+/`) with `#`-comments stripped by a separate ignored terminal; the parser (grammar rule for `program`) skips stray leading NEWLINEs.
Every assignment statement (including reassignment) starts with the `let` keyword, so `assignment` and `expr_stmt` are unambiguous to an LALR(1) parser without extra lookahead.

### Lark grammar draft (`moose/grammar.lark`)
```
?start: block

block: _NEWLINE* (statement _NEWLINE*)*

?statement: if_stmt | func_def | return_stmt | assignment | expr_stmt

if_stmt: "if" expression ":" block ("else" ":" block)? "end"
func_def: "def" NAME "(" params ")" ":" block "end"
params: (NAME ("," NAME)*)?
return_stmt: "return" expression?
assignment: "let" NAME "=" expression
expr_stmt: expression

?expression: or_expr

?or_expr: and_expr
        | or_expr "or" and_expr     -> or_

?and_expr: not_expr
         | and_expr "and" not_expr  -> and_

?not_expr: comparison
         | "not" not_expr           -> not_

?comparison: term
           | comparison "==" term   -> eq
           | comparison "!=" term   -> ne
           | comparison "<" term    -> lt
           | comparison ">" term    -> gt
           | comparison "<=" term   -> le
           | comparison ">=" term   -> ge

?term: factor
     | term "+" factor -> add
     | term "-" factor -> sub

?factor: unary
       | factor "*" unary -> mul
       | factor "/" unary -> div
       | factor "%" unary -> mod

?unary: call
      | "-" unary -> neg

?call: primary
     | call "(" arguments ")" -> call

arguments: (expression ("," expression)*)?

?primary: NUMBER            -> number
        | "true"            -> true
        | "false"           -> false
        | NAME              -> variable
        | "(" expression ")"

NAME: /[a-zA-Z_][a-zA-Z0-9_]*/
NUMBER: /\d+(\.\d+)?/
_NEWLINE: /(\r?\n)+/
COMMENT: /#[^\n]*/
%ignore /[ \t]+/
%ignore COMMENT
```
Notes:
- `_NEWLINE` (leading underscore) is filtered from the tree automatically by Lark but still consumed as a real terminal, so it enforces one-statement-per-line without cluttering the parse tree; the regex accepts `\r\n` too for Windows-authored source files.
- Keywords (`if`, `else`, `end`, `def`, `return`, `let`, `true`, `false`, `and`, `or`, `not`) are written as inline string literals; Lark auto-creates anonymous terminals for them and — because Lark prioritizes literal string terminals over the `NAME` regex terminal — they're matched as keywords rather than identifiers even though `NAME`'s regex would also match them.
- **Operators/keywords never survive into the tree.** Lark elides *every* anonymous string-literal terminal from the parse tree (punctuation like `(`/`:` and keyword-shaped literals like `"if"`/`"true"` alike), so a naive `term (("+"|"-") factor)*`-style repetition rule would leave `ast_builder.py` with no way to tell `+` from `-`. The grammar instead uses **left-recursive rules with a distinct `-> alias` per alternative** (`add`/`sub`, `mul`/`div`/`mod`, `eq`/`ne`/`lt`/`gt`/`le`/`ge`, `and_`/`or_`/`not_`, `neg`, `call`) — the same pattern as Lark's own calculator example — so the Transformer dispatches on tree/alias name instead of inspecting a (missing) operator token. Aliased alternatives are exempt from `?`-collapsing even when they have a single child, so e.g. `"not" not_expr -> not_` still produces a `not_` node instead of vanishing.
- `block`, `params`, and `arguments` are deliberately **not** prefixed with `?`, so they always materialize as their own tree node (even when empty, e.g. a zero-arg call or a no-param function). Without this, an optional `else` block or a variable-length `then`/`else` statement list would flatten into one undifferentiated list of children with no marker for where one branch ends and the other begins; `if_stmt`/`func_def`/`call` end up with a fixed, small number of children instead (verified via `tree.pretty()` against `if/else`, `def`, and nested-call snippets).
- Rules prefixed with `?` (the operator-precedence chain, `statement`, `primary`) are inlined by Lark whenever an alternative has no alias and exactly one child, which keeps the parse tree close to the final AST shape and reduces boilerplate in `ast_builder.py`.
- `parser="lalr"` is used when constructing the `Lark` instance for speed and deterministic error locations; confirmed (Phase 0 spike) that this grammar builds with no LALR conflicts and produces the expected trees for `if/else`, `def`/recursive `call`, and full operator-precedence chains (`not a and b or c`, `1 + 2 * 3`). If a future grammar change (e.g. v2 features) introduces a conflict LALR can't resolve, fall back to `parser="earley"` for that rule set instead of hand-fixing the grammar.

## Proposed project structure
```
mooselite/
  pyproject.toml            # package "moose", py313, lark runtime dep, pytest dev dep, console_script "moose"
  moose/
    __init__.py
    __main__.py             # `python -m moose script.moose` or no-arg -> REPL
    grammar.lark              # Lark grammar: terminals + rules per the draft above
    ast_nodes.py              # dataclasses: NumberLiteral, BoolLiteral, VariableExpr, AssignExpr,
                              #   BinaryExpr, LogicalExpr, UnaryExpr, CallExpr,
                              #   ExpressionStmt, IfStmt, FuncDefStmt, ReturnStmt
    ast_builder.py             # lark.Transformer: parse tree -> ast_nodes dataclasses
    parser.py                 # builds the Lark(parser="lalr") instance from grammar.lark, exposes parse(source)
    environment.py             # Environment class: define/get/assign, parent chain for closures
    interpreter.py              # Interpreter: execute()/evaluate() via match-statement dispatch,
                                 #   MooseFunction class, ReturnSignal(Exception) for unwinding
    errors.py                   # MooseSyntaxError, MooseRuntimeError (message + line); MooseSyntaxError
                                 #   is raised from lark.exceptions.UnexpectedInput caught in parser.py
    repl.py                     # REPL loop, multi-line input buffering until matching `end`s close
  examples/
    hello.moose                # variables + arithmetic + print
    max.moose                  # if/else demo
    fib.moose                  # recursive function, comparisons, arithmetic
  tests/
    test_grammar.py
    test_parser.py
    test_interpreter.py
    test_examples.py           # runs each example .moose file end-to-end, asserts stdout
```
Note: current [.gitignore](.gitignore) ignores `examples/` and `docs/` — needs updating so example scripts get tracked by git (flagged as a to-do in Phase 0).

## Steps

### Phase 0: Scaffolding
1. Create `pyproject.toml` (package `moose`, requires-python >=3.13, `lark` as a runtime dependency, pytest as dev dependency, optional console_script entry point `moose = moose.__main__:main`).
2. Create empty `moose/` package files listed above (stubs) and `tests/`, `examples/` directories.
3. Edit [.gitignore](.gitignore) to remove the `examples/` and `docs/` ignore entries (currently blocks tracking the example scripts this plan creates).

### Phase 1: Lark grammar & parser wrapper — *depends on Phase 0*
4. Write `moose/grammar.lark` (drafted and validated above via a Phase-0 spike: built with `Lark(parser="lalr")` with no conflicts, `tree.pretty()` inspected for if/else, def+recursive-call, and full `not`/`and`/`or`/arithmetic snippets). Broken into pieces:
   - 4.1 Terminals: `NAME`, `NUMBER`, `_NEWLINE` (accepts `\r\n`), `COMMENT`; `%ignore` inline whitespace and `COMMENT`.
   - 4.2 Statement-level rules: `block`, `if_stmt`, `func_def` + `params`, `return_stmt`, `assignment`, `expr_stmt`. `block`/`params`/`arguments` stay un-prefixed (no `?`) so they always materialize as their own node — this is what lets `ast_builder.py` tell `if_stmt`'s then-block apart from its else-block, and `func_def`'s param list apart from its body, instead of getting one flattened list of children.
   - 4.3 Expression precedence chain: left-recursive rules with a distinct `-> alias` per operator (`or_`/`and_`/`not_`, `eq`/`ne`/`lt`/`gt`/`le`/`ge`, `add`/`sub`, `mul`/`div`/`mod`, `neg`, `call`) plus `primary` (`number`/`true`/`false`/`variable`/parenthesized group). Aliases are required because Lark elides anonymous string-literal tokens (keywords *and* operators) from the tree.
   - 4.4 Re-run the spike (or fold it into `test_grammar.py`, see step 6) whenever the grammar changes, to catch new LALR conflicts immediately rather than discovering them via a confusing runtime parse error.

5. Implement `parser.py` (a first draft already exists in the repo — treat the sub-steps below as the fix-up list for it):
   - 5.1 Load the grammar text via a path relative to this module, not the process's cwd: `Path(__file__).with_name("grammar.lark").read_text(encoding="utf-8")`. The current draft's bare `open("grammar.lark")` only works if the interpreter happens to be launched from inside `moose/`, and breaks for `python -m moose`, the console-script entry point, or running tests from the repo root — fix this first.
   - 5.2 Build one module-level `Lark` instance at import time: `Lark(grammar_text, parser="lalr", propagate_positions=True)`. `propagate_positions=True` is missing from the current draft; without it, every `Tree`'s `.meta.line`/`.meta.column` is unset, which breaks the `line` field Phase 2's `ast_builder.py` needs on every AST dataclass, and breaks line numbers in error messages.
   - 5.3 Expose a low-level `parse(source: str) -> Tree` (thin wrapper over the module-level parser's `.parse()`) so `test_grammar.py` can inspect raw parse trees without going through the AST transformer.
   - 5.4 Expose the real entry point `parse_program(source: str) -> Program`: call `parse()`, then run the result through `ast_builder.AstBuilder().transform(tree)`. Move the `ast_builder` import to module level once Phase 2 creates it — the current draft imports it lazily inside the function on every call, which is unnecessary once the circular-import risk is checked (ast_builder only needs ast_nodes, not parser, so no cycle).
   - 5.5 Wrap the underlying `.parse()` call in `try/except lark.exceptions.UnexpectedInput as e` (this base class covers both `UnexpectedToken` and `UnexpectedCharacters`) and re-raise as `MooseSyntaxError`. Build the message from `e.line`, `e.column`, and `e.get_context(source)` (shows the offending source line with a `^` pointer); the current draft has no error translation at all, so a malformed script currently surfaces a raw Lark traceback instead of a friendly `Error [line N]: ...`.
   - 5.6 Decide the message format up front so `test_grammar.py` (step 6) and `__main__.py` (Phase 5) can rely on it, e.g. `f"unexpected input at line {e.line}: {e.get_context(source).strip()}"`, passed as the `message` to `MooseSyntaxError(message, line=e.line)`.

6. Write `tests/test_grammar.py`:
   - 6.1 Positive cases: run each snippet already validated in the spike (arithmetic precedence, if/else, def + recursive call, `not`/`and`/`or` chain, zero-arg call) through `parser.parse()` and assert no exception plus a sanity check on tree shape (e.g. `tree.data == "block"`, expected child count).
   - 6.2 Keyword-vs-identifier collision: parse a snippet with identifiers that contain a keyword as a substring (`lettuce`, `ifx`, `endpoint`) and confirm each lexes as a single `NAME`, not split around the embedded keyword.
   - 6.3 Comment handling: a comment-only line and a trailing end-of-line comment after a statement should both parse with no extra/missing children and without requiring a blank line afterward.
   - 6.4 Negative cases: assert `parser.parse()`/`parse_program()` raises `MooseSyntaxError` for an unterminated `if` (missing `end`), a stray unexpected character (e.g. `@`), and an `else` with no matching `if`; assert the raised error's `.line` matches the expected source line for each case.

### Phase 2: AST nodes & transformer — *depends on Phase 0, parallel with Phase 1*
7. Define all AST dataclasses in ast_nodes.py per the grammar (expression nodes + statement nodes). Keep each node a plain `@dataclass` with a `line` field for error reporting.
8. Implement `AstBuilder(lark.Transformer)` in ast_builder.py: one method per grammar rule name (`assignment`, `if_stmt`, `func_def`, `return_stmt`, `expr_stmt`, `number`, `true`, `false`, `variable`, and one per binary/logical/unary operator rule) that builds the matching ast_nodes dataclass from the rule's children, pulling `line` from the Lark `Token`/`Tree.meta.line`.

### Phase 3: Parser integration tests — *depends on Phases 1 & 2*
9. Write test_parser.py: feed real source snippets through `parser.parse_program()` and assert resulting AST shapes for each construct (assignment, if/else, def/return, expressions with correct precedence — e.g. `1 + 2 * 3` produces a `BinaryExpr` tree with `*` nested inside `+`, not the reverse).
10. Confirm `MooseSyntaxError` messages surfaced through `parse_program()` include a 1-based line number and a short excerpt, e.g. "Error [line 3]: unexpected token 'end', expected ...".

### Phase 4: Environment & Interpreter — *depends on Phase 3*
11. Implement `Environment` in environment.py: `define`, `get`, `assign`, with optional `parent` for lexical scoping; `get`/`assign` walk up the parent chain; raise `MooseRuntimeError` on undefined names.
12. Implement `Interpreter` in interpreter.py:
    - `evaluate(expr, env)` dispatch (Python `match` statement) for all expression node types; arithmetic ops (+ - * / % with divide-by-zero -> `MooseRuntimeError`), comparisons, short-circuit `and`/`or`, unary `-`/`not`, `is_truthy()` helper.
    - `execute(stmt, env)` dispatch for statements: `let` assignment (always `env.define()` in the current env, since every assignment repeats `let` — this also allows shadowing), `IfStmt` (evaluate condition, run chosen branch's statements in the *same* env — no new scope), `FuncDefStmt` (build `MooseFunction(name, params, body, closure_env)`, store in env), `ReturnStmt` (raise internal `ReturnSignal(value)`).
    - Function calls: new child `Environment` parented to the function's closure (not the call site) for correct lexical scoping; bind args to params with arity check -> `MooseRuntimeError` on mismatch; run body statements catching `ReturnSignal` to get the return value; implicit `None` return if body completes without `return`.
    - Register built-in `print(*args)` in the global environment as a native callable.
13. Write test_interpreter.py: run small programs end-to-end (arithmetic precedence, variable reassignment, if/else both branches, recursive function like factorial/fibonacci, closures) and assert on captured stdout / returned values.

### Phase 5: CLI & REPL — *depends on Phase 4*
14. `__main__.py`: `main()` reads argv; if a `.moose` file path is given, read source, `parser.parse_program()` -> interpret it; otherwise launch REPL. Catch `MooseSyntaxError`/`MooseRuntimeError` at the top level and print `Error [line N]: message` instead of a raw Python traceback.
15. `repl.py`: prompt loop (`>>> `), buffer multi-line input by counting unmatched `if`/`def` vs `end` keywords before attempting to parse/interpret a complete chunk; auto-print the value of bare expression statements (Python REPL-style).

### Phase 6: Examples & end-to-end tests — *depends on Phase 5*
16. Write examples/hello.moose, examples/max.moose, examples/fib.moose exercising every v1 feature (all variable assignments use `let`).
17. Write test_examples.py: execute each example file through the real CLI entry point and assert expected stdout.
18. Run the full pytest suite; run each example manually via `python -m moose examples/<file>.moose`; manually exercise the REPL for a couple of interactions.

**Relevant files**
- `pyproject.toml` — new, package metadata + `lark` runtime dependency + pytest dev dependency + console_script
- `.gitignore` — remove `examples/`/`docs/` ignore entries
- `moose/grammar.lark`, `moose/parser.py` — Lark grammar + parser wrapper (tokenizing + parsing)
- `moose/ast_nodes.py`, `moose/ast_builder.py` — parse tree -> AST
- `moose/environment.py`, `moose/interpreter.py` — evaluation
- `moose/errors.py` — `MooseSyntaxError`, `MooseRuntimeError`
- `moose/__main__.py`, `moose/repl.py` — CLI/REPL
- `examples/*.moose`, `tests/test_*.py` — validation

**Verification**
1. `pytest` from repo root — all unit + example tests pass.
2. `python -m moose examples/fib.moose` — prints expected Fibonacci sequence/value.
3. `python -m moose` (REPL) — manually type `let x = 3`, `let y = 4`, `print(x + y)` -> expect `7`; test an `if/else` and a `def`/recursive call interactively.
4. Manually trigger error paths (divide by zero, undefined variable, mismatched `end`) and confirm friendly `Error [line N]: ...` output, not a raw traceback.

**Scope boundaries**
- Included: variables, arithmetic, comparisons, booleans, if/else, functions (with recursion + closures), comments, REPL, file execution, `end`-delimited blocks.
- Excluded from v1 (by explicit user choice): strings, lists/arrays, while/for loops, indentation-based blocks, bytecode compilation. Architecture (AST + tree-walking) makes these straightforward to add later without redesigning the core.

**Further Considerations**
1. `.gitignore` currently excludes `examples/` and `docs/` — this plan assumes that was unintentional/leftover and will un-ignore `examples/` (docs/ left untouched since no docs are planned). Flag if this was intentional.
