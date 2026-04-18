# contingency-dsl2procedure

:jp: [日本語版 README](README.ja.md)

Compiler from [contingency-dsl](https://github.com/OperantKit/contingency-dsl) JSON AST to academic paper Method sections.

Zero external dependencies. Works with any parser that emits conformant `ast-schema.json`.

```python
from contingency_dsl2procedure import compile_method

# Input: plain dict conforming to contingency-dsl/ast-schema.json
ast = {
    "type": "Program",
    "param_decls": [],
    "bindings": [],
    "schedule": {
        "type": "Compound",
        "combinator": "Conc",
        "components": [
            {"type": "Atomic", "dist": "V", "domain": "I", "value": 30.0, "time_unit": "s"},
            {"type": "Atomic", "dist": "V", "domain": "I", "value": 60.0, "time_unit": "s"},
        ],
    },
}

# JEAB (English, default)
method = compile_method(ast, style="jeab")
print(method.procedure)
# Responses were reinforced under a concurrent VI 30-s VI 60-s schedule.

# J-ABA (Japanese)
method_ja = compile_method(ast, style="jaba")
print(method_ja.procedure)
# 並立 VI 30-s VI 60-sスケジュールに従って反応が強化された。

# References are auto-collected
print(method.references)
# (Reference(key='fleshler_hoffman_1962', ...),)
```

