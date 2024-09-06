# import packages/modules
import sympy as sp


class EquationBuilder:
    def __init__(self, symbol_string):
        # Create symbols and store them in the class dictionary
        self.symbols = sp.symbols(symbol_string)
        self.symbol_names = symbol_string.split()
        self._store_symbols()

    def _store_symbols(self):
        # Store symbols as class attributes
        for name, symbol in zip(self.symbol_names, self.symbols):
            setattr(self, name, symbol)

    def remove_symbols(self):
        # Remove symbols from class attributes
        for name in self.symbol_names:
            if hasattr(self, name):
                delattr(self, name)

    def get_symbols(self):
        # Return the symbols as a dictionary
        return {name: getattr(self, name) for name in self.symbol_names if hasattr(self, name)}

    def evaluate_expression(self, expression_string, **kwargs):
        # Create the symbolic expression from the string
        expression = sp.sympify(expression_string)

        # Substitute values into the expression
        result = expression.subs(kwargs)

        return result
