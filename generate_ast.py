import sys

TAB = "    "

expr_types = {
    "Assign"  : ["name", "value"],
    "Binary"  : ["left", "operator", "right"],
    "Call"    : ["callee", "paren", "arguments"],
    "Get"     : ["object_", "name"],
    "Grouping": ["expression"],
    "Literal" : ["value"],
    "Logical" : ["left", "operator", "right"],
    "Set"     : ["object_", "name", "value"],
    "Super"   : ["keyword", "method"],
    "This"    : ["keyword"],
    "Unary"   : ["operator", "right"],
    "Variable": ["name"],
}

stmt_types = {
    "Block"      : ["statements"],
    "Class"      : ["name", "superclass", "methods"],
    "Expression" : ["expression"],
    "Function"   : ["name", "params", "body"],
    "If"         : ["condition", "then_branch", "else_branch"],
    "Print"      : ["expression"],
    "Return"     : ["keyword", "value"],
    "Var"        : ["name", "initializer"],
    "While"      : ["condition", "body"],
}

def define_ast(output_dir, base_name, types):
    filepath = f"{output_dir}/{base_name.lower()}.py"
    with open(filepath, "w") as f:
        f.write("from abc import ABC, abstractmethod\n")
        f.write("\n\n")
        
        define_visitorclass(f, base_name, types)
        f.write("\n\n")

        define_baseclass(f, base_name)

        for cls_name, fields in types.items():
            define_type(f, base_name, cls_name, fields)


def define_visitorclass(f, base_name, types):
    functions = [
        f"{TAB}def visit_{field.lower()}(expr): raise NotImplementedError\n" \
        for field in types.keys()
    ]
    f.write(f"class {base_name}Visitor():\n")
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
    define_ast(output_dir, "Stmt", stmt_types)
