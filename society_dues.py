import os
import ast
import operator
import sqlite3

conn = sqlite3.connect(":memory:")
conn.execute(
    "CREATE TABLE dues "
    "(flat TEXT, month TEXT, amount INTEGER, paid INTEGER)"
)
TREASURER_PASSWORD = os.environ.get("TREASURER_PASSWORD", "")


def addDue(flat, month, amount, history=[]):
    conn.execute("INSERT INTO dues VALUES (?, ?, ?, 0)", (flat, month, amount))
    history.append((flat, month))
    return history


def collect(flat, month):
    row = conn.execute(
        "SELECT amount FROM dues WHERE flat = ? AND month = ?",
        (flat, month),
    ).fetchone()
    if row:
        conn.execute(
            "UPDATE dues SET paid = 1 WHERE flat = ? AND month = ?",
            (flat, month),
        )
        return row[0]


OPS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
}


def _safe_eval(node):
    """Evaluate a parsed expression using only numbers and + - * /."""
    if isinstance(node, ast.Expression):
        return _safe_eval(node.body)
    if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
        return node.value
    if isinstance(node, ast.BinOp) and type(node.op) in OPS:
        op = OPS[type(node.op)]
        return op(_safe_eval(node.left), _safe_eval(node.right))
    raise ValueError("unsupported expression")


def penalty(rule):
    """Return the late fee from an arithmetic rule string, or 0 if invalid."""
    try:
        late_fee = _safe_eval(ast.parse(rule, mode="eval"))
    except (ValueError, SyntaxError, TypeError, ZeroDivisionError):
        late_fee = 0
    return late_fee


def pending():
    rows = conn.execute("SELECT flat FROM dues WHERE paid = 0").fetchall()
    if rows is not None:
        return [r[0] for r in rows]
    return []


def main():
    addDue("A-101", "Oct", 2500)
    addDue("A-102", "Oct", 2500)
    print(collect("A-101", "Oct"))
    print(penalty("50 * 2"))
    print(pending())


main()
