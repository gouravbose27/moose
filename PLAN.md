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
Multi-char operators must be lexed greedily before single-char ones: `==` before `=`, `<=`/`>=` before `<`/`>`, `!=` only as a pair (no bare `!`).
NEWLINE is a real token ending a statement; consecutive blank/comment-only lines collapse to one NEWLINE; parser skips stray leading NEWLINEs.
Every assignment statement (including reassignment) starts with the `let` keyword, so `assignment` and `expr_stmt` are unambiguous to the parser without lookahead.

## Proposed project structure
```
mooselite/
  pyproject.toml            # package "moose", py313, pytest dev dep, console_script "moose"
  moose/
    __init__.py
    __main__.py             # `python -m moose script.moose` or no-arg -> REPL
    tokens.py                # TokenType enum + Token dataclass (type, lexeme, value, line)
    lexer.py                 # Lexer.scan_tokens() (keywords include `let`)
    ast_nodes.py              # dataclasses: NumberLiteral, BoolLiteral, VariableExpr, AssignExpr,
                              #   BinaryExpr, LogicalExpr, UnaryExpr, CallExpr,
                              #   ExpressionStmt, IfStmt, FuncDefStmt, ReturnStmt
    parser.py                 # Parser: recursive descent + precedence climbing per grammar above
    environment.py             # Environment class: define/get/assign, parent chain for closures
    interpreter.py              # Interpreter: execute()/evaluate() via match-statement dispatch,
                                 #   MooseFunction class, ReturnSignal(Exception) for unwinding
    errors.py                   # MooseSyntaxError, MooseRuntimeError (message + line)
    repl.py                     # REPL loop, multi-line input buffering until matching `end`s close
  examples/
    hello.moose                # variables + arithmetic + print
    max.moose                  # if/else demo
    fib.moose                  # recursive function, comparisons, arithmetic
  tests/
    test_lexer.py
    test_parser.py
    test_interpreter.py
    test_examples.py           # runs each example .moose file end-to-end, asserts stdout
```
Note: current [.gitignore](.gitignore) ignores `examples/` and `docs/` — needs updating so example scripts get tracked by git (flagged as a to-do in Phase 0).

## Steps

### Phase 0: Scaffolding
1. Create `pyproject.toml` (package `moose`, requires-python >=3.13, pytest as dev dependency, optional console_script entry point `moose = moose.__main__:main`).
2. Create empty `moose/` package files listed above (stubs) and `tests/`, `examples/` directories.
3. Edit [.gitignore](.gitignore) to remove the `examples/` and `docs/` ignore entries (currently blocks tracking the example scripts this plan creates).

### Phase 1: Tokens & Lexer — *depends on Phase 0*
4. Define `TokenType` enum and `Token` dataclass in tokens.py.
5. Implement `Lexer` in lexer.py: char-by-char scan producing NUMBER (int/float), IDENTIFIER, keywords (let/if/else/end/def/return/true/false/and/or/not), operators (= == != < > <= >= + - * / % ( ) , :), NEWLINE, EOF. Skip whitespace and `#`-comments. Raise `MooseSyntaxError` on unexpected characters (with line number).
6. Write test_lexer.py: tokenize small snippets (numbers, identifiers, operators, comments) and assert exact token sequences.

### Phase 2: AST nodes — *depends on Phase 0, parallel with Phase 1*
7. Define all AST dataclasses in ast_nodes.py per the grammar (expression nodes + statement nodes). Keep each node a plain `@dataclass` with a `line` field for error reporting.

### Phase 3: Parser — *depends on Phases 1 & 2*
8. Implement `Parser` in parser.py: one method per grammar rule, precedence-climbing for expressions (or -> and -> not -> comparison -> term -> factor -> unary -> call -> primary), block parsing (statements until `else`/`end`), assignment statements recognized unambiguously by a leading `let` keyword.
9. Raise `MooseSyntaxError` with a clear "expected X, got Y at line N" message on malformed input.
10. Write test_parser.py: feed token lists (or lex real source) and assert resulting AST shapes for each construct (assignment, if/else, def/return, expressions with correct precedence).

### Phase 4: Environment & Interpreter — *depends on Phase 3*
11. Implement `Environment` in environment.py: `define`, `get`, `assign`, with optional `parent` for lexical scoping; `get`/`assign` walk up the parent chain; raise `MooseRuntimeError` on undefined names.
12. Implement `Interpreter` in interpreter.py:
    - `evaluate(expr, env)` dispatch (Python `match` statement) for all expression node types; arithmetic ops (+ - * / % with divide-by-zero -> `MooseRuntimeError`), comparisons, short-circuit `and`/`or`, unary `-`/`not`, `is_truthy()` helper.
    - `execute(stmt, env)` dispatch for statements: `let` assignment (always `env.define()` in the current env, since every assignment repeats `let` — this also allows shadowing), `IfStmt` (evaluate condition, run chosen branch's statements in the *same* env — no new scope), `FuncDefStmt` (build `MooseFunction(name, params, body, closure_env)`, store in env), `ReturnStmt` (raise internal `ReturnSignal(value)`).
    - Function calls: new child `Environment` parented to the function's closure (not the call site) for correct lexical scoping; bind args to params with arity check -> `MooseRuntimeError` on mismatch; run body statements catching `ReturnSignal` to get the return value; implicit `None` return if body completes without `return`.
    - Register built-in `print(*args)` in the global environment as a native callable.
13. Write test_interpreter.py: run small programs end-to-end (arithmetic precedence, variable reassignment, if/else both branches, recursive function like factorial/fibonacci, closures) and assert on captured stdout / returned values.

### Phase 5: CLI & REPL — *depends on Phase 4*
14. `__main__.py`: `main()` reads argv; if a `.moose` file path is given, read source, lex -> parse -> interpret it; otherwise launch REPL. Catch `MooseSyntaxError`/`MooseRuntimeError` at the top level and print `Error [line N]: message` instead of a raw Python traceback.
15. `repl.py`: prompt loop (`>>> `), buffer multi-line input by counting unmatched `if`/`def` vs `end` keywords before attempting to lex/parse/interpret a complete chunk; auto-print the value of bare expression statements (Python REPL-style).

### Phase 6: Examples & end-to-end tests — *depends on Phase 5*
16. Write examples/hello.moose, examples/max.moose, examples/fib.moose exercising every v1 feature (all variable assignments use `let`).
17. Write test_examples.py: execute each example file through the real CLI entry point and assert expected stdout.
18. Run the full pytest suite; run each example manually via `python -m moose examples/<file>.moose`; manually exercise the REPL for a couple of interactions.

**Relevant files**
- `pyproject.toml` — new, package metadata + pytest dependency + console_script
- `.gitignore` — remove `examples/`/`docs/` ignore entries
- `moose/tokens.py`, `moose/lexer.py` — tokenizing
- `moose/ast_nodes.py`, `moose/parser.py` — parsing
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
