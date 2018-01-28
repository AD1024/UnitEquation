from enum import Enum
from ExpressionEvaluator import *
import Reader
import math

'''
Syntax: 
<?><Unit> <operator> <num><Unit> = <num><Unit> <operator> <?><Unit>
'''

UNIT_LIST = ['mi', 'km', 'm', 'dm', 'cm', 'ft', 'yd', 'in', 'mm']


class Unit(Enum):
    mi = 'mi'
    km = 'km'
    m = 'm'
    dm = 'dm'
    cm = 'cm'
    ft = 'ft'
    yd = 'yd'
    inn = 'in'
    mm = 'mm'


def to_meter(value, unit):
    return {
        Unit.cm: lambda: value / 100,
        Unit.m: lambda: value,
        Unit.dm: lambda: value / 10,
        Unit.km: lambda: value * 1000,
        Unit.ft: lambda: value * 0.3048,
        Unit.yd: lambda: value * 0.9144,
        Unit.inn: lambda: value * 0.0254,
        Unit.mi: lambda: value * 1609,
        Unit.mm: lambda: value * 0.001,
    }[unit]()


def meter_to(value, unit):
    return {
        Unit.cm: lambda: value * 100,
        Unit.m: lambda: value,
        Unit.dm: lambda: value * 10,
        Unit.km: lambda: value / 1000,
        Unit.ft: lambda: value / 0.3048,
        Unit.yd: lambda: value / 0.9144,
        Unit.inn: lambda: value / 0.0254,
        Unit.mi: lambda: value / 1609,
        Unit.mm: lambda: value / 0.001,
    }[unit]()


def unify_expression(exp):
    ret = ''
    query_unit = None
    leading_symbol = None
    reader = Reader.new_instance(exp)

    def read_num(leading):
        ans = leading
        while reader.has_next() and reader.get_cursor_data().isdigit():
            ans += reader.next()
        if reader.get_cursor_data() == '.':
            ans += reader.next()
            while reader.has_next() and reader.get_cursor_data().isdigit():
                ans += reader.next()
        return float(ans)

    def read_unit():
        ans = ''
        while reader.has_next() and 'a' <= reader.get_cursor_data().lower() <= 'z':
            ans += reader.next().lower()
        return ans

    while reader.has_next():
        ch = reader.next()
        if ch == '-' and reader.get_cursor() == 1:
            ret += '-'
            continue
        elif ch.isdigit():
            v = read_num(ch)
            u = read_unit()
            if u not in UNIT_LIST:
                raise SyntaxError('Unit cannot be recognized @ {}'.format(reader.get_cursor() - len(u) + 1))
            v = to_meter(v, Unit(u))
            ret = ret + '{}'.format(v)
        elif ch == '?':
            leading_symbol = reader.get_prev_data(2)
            query_unit = Unit(read_unit())
        elif ch == '-' or ch == '+':
            if reader.get_cursor_data() != '?' and reader.get_prev_data(step=3) != '?' \
                    and reader.get_prev_data(step=4) != '?':
                ret += ch
        else:
            ret += ch
    if leading_symbol is None:
        leading_symbol = '+'
    return (ret, query_unit, leading_symbol) if query_unit and leading_symbol else ret


def eval_expression(expr):
    return Evaluator(ExprTreeConstructor(expr).build()).eval()


def print_ans(expr, ans):
    print('ans:', end=' ')
    ans_pos = expr.find('?')
    output = None
    if ans < 0:
        if ans_pos != 0:
            if expr[ans_pos - 1] == '+':
                output = '{}{}{}'.format(expr[:ans_pos - 1], ans, expr[ans_pos + 1:])
            else:
                ans = -ans
                output = '{}{}{}'.format(expr[:ans_pos - 1] + '+', ans, expr[ans_pos + 1:])
            print(output)
            return
    output = expr.replace('?', '{}'.format(ans))
    print(output)


def main():
    print('Input the expression(function or equation):')
    while 1:
        print('=>', end=' ')
        expr = ''
        try:
            expr = input()
        except EOFError:
            exit(0)
        expr = expr.replace(' ', '')
        eq_pos = expr.find('=')
        rexpr = expr[eq_pos + 1:]
        lexpr = expr[:eq_pos]
        if rexpr.find('?') == lexpr.find('?') == -1 or rexpr.find('?') != -1 and lexpr.find('?') != -1:
            print('Error Expression')
            return -1
        if lexpr.find('?') == -1:
            rexpr, lexpr = (lexpr, rexpr)
        lexpr, query_unit, leading_symbol = unify_expression(lexpr)
        rexpr = unify_expression(rexpr)
        if lexpr == '':
            lexpr = '0'
        if rexpr == '':
            rexpr = '0'
        # print(lexpr, rexpr, sep=',')
        raw_value = {
            '+': lambda: eval_expression(rexpr) - eval_expression(lexpr),
            '-': lambda: eval_expression(lexpr) - eval_expression(rexpr),
        }[leading_symbol]()
        query_ans = meter_to(raw_value, query_unit)
        print_ans(expr, round(query_ans, 6))


main()
