from ast_nodes import *

def transpile(node, indent=0):
    prefix = " " * indent

    if isinstance(node, CodeBlock):
        return "\n".join(
            transpile(statement, indent)
            for statement in node.statements
        )

    if isinstance(node, LetStatement):
        return f"{prefix}{str(node.name)} = {transpile(node.value)}"

    if isinstance(node, DisplayStatement):
        return f"{prefix}print({transpile(node.value)})"

    if isinstance(node, IfStatement):
        lines = [
            f"{prefix}if {transpile(node.condition)}:"
        ]
        if not hasattr(node.body, "__iter__"):
            lines.append(f"{transpile(node.body, indent + 4)}")
        else:
            lines.extend(
                transpile(statement, indent + 4)
                for statement in node.body 
            )

        if node.orelse:
            lines.append(f"{prefix}else:")
            if not hasattr(node.orelse, "__iter__"):
                lines.append(f"{transpile(node.orelse, indent + 4)}")
            else:
                lines.extend(
                    transpile(statement, indent + 4)
                    for statement in node.orelse
                )

        return "\n".join(lines)

    if isinstance(node, Number):
        return str(node.value)

    if isinstance(node, String):
        return repr(node.value)

    if isinstance(node, Name):
        return str(node.name)

    if isinstance(node, Boolean):
        return True if node.value else False

    raise TypeError(f"Unsupported AST node: {type(node).__name__}")