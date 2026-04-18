# contingency-dsl2procedure

:gb: [English README](README.md)

[contingency-dsl](https://github.com/OperantKit/contingency-dsl) の JSON AST から学術論文の Method セクションへ変換するコンパイラ。

外部依存ゼロ。適合する `ast-schema.json` を生成する任意のパーサと連携可能。

```python
from contingency_dsl2procedure import compile_method

# 入力: contingency-dsl/ast-schema.json に適合する素の dict
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

# JEAB スタイル（英語、デフォルト）
method = compile_method(ast, style="jeab")
print(method.procedure)
# Responses were reinforced under a concurrent VI 30-s VI 60-s schedule.

# J-ABA スタイル（日本語）
method_ja = compile_method(ast, style="jaba")
print(method_ja.procedure)
# 並立 VI 30-s VI 60-sスケジュールに従って反応が強化された。

# 参考文献は自動収集される
print(method.references)
# (Reference(key='fleshler_hoffman_1962', ...),)
```

