import sys

TAB = "    "

expr_types = {
    "Binary"  : ["left", "operator", "right"],
    "Grouping": ["expression"],
    "Literal" : ["value"],
    "Unary"   : ["operator", "right"]
}

def define_ast(path, base_name, types):
    with open(path, "w") as f:
        f.write("from abc import ABC, abstractmethod\n")
        f.write("\n\n")
        
        define_visitorclass(f)
        f.write("\n\n")

        define_baseclass(f, base_name)

        for cls_name, fields in expr_types.items():
            define_type(f, base_name, cls_name, fields)


def define_visitorclass(f):
    functions = [
        f"{TAB}def visit_{expr_type.lower()}(expr): raise NotImplementedError\n" \
        for expr_type in expr_types.keys()
    ]
    f.write(f"class ExprVisitor():\n")
    f.writelines(functions)


def define_baseclass(f, base_name):
    f.writelines([
        f"class {base_name}(ABC):\n",
        f"{TAB}@abstractmethod\n",
        f"{TAB}def accept(self):\n",
        f"{TAB}{TAB}raise NotImplementedError\n\n\n"
    ])


def define_type(f, base_name, cls_name, fields):
    f.write(f"class {cls_name}({base_name}):\n")

    # init
    f.write(f"{TAB}def __init__(self, {', '.join(fields)}):\n")
    init_stmts = [f"{TAB}{TAB}self.{field} = {field}\n" for field in fields]
    f.writelines(init_stmts)
    f.write("\n")

    # accept method
    f.writelines([
        f"{TAB}def accept(self, visitor):\n",
        f"{TAB}{TAB}return visitor.visit_{cls_name.lower()}(self)\n"
    ])

    f.write("\n\n")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: generate_ast <output directory")
        sys.exit(64)

    output_dir = sys.argv[1]
    define_ast(output_dir, "Expr", expr_types)
