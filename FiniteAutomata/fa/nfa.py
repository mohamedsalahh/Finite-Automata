import copy
from typing import Set, Tuple, TypeVar
from AlgebraicExpressionParser import Expression
from FiniteAutomata.exceptions.Exceptions import *
from graphviz import Digraph


NFA = TypeVar('NFA')


class NFA:
    def __init__(self, regex: str) -> None:
        """
        regex: the regex that would be converted into nfa
        regex type: str
        """
        self.regex = regex

    @property
    def regex(self) -> Expression:
        return self._regex

    @regex.setter
    def regex(self, regex: str) -> None:
        regex = self._remove_spaces_from_string(regex)
        regex = self._insert_concatenate_operator(regex)
        self._regex = Expression(expression=regex, operators={
            '+', '&', '*'}, operators_info={'+': (2, 1), '&': (2, 2), '*': (1, 3)}, operators_associativity={'+': 'LR', '&': 'LR', '*': 'LR'}, variables=self._get_regex_symbols(regex))
        self._construct_transitions_table()

    def __str__(self) -> str:
        return f"< Symbols: {self.symbols}\n  States: {self.states}\n  Transitions Table: {self.transitions_table}\n  Start State: {self.start_state}\n  Final State: {self.final_state} >"

    def __repr__(self) -> str:
        return f"NFA('{self.regex.expression}')"

    def __iter__(self):
        for state, transitions in self.transitions_table.items():
            yield (state, transitions)
    
    def copy(self) -> NFA:
        """Create a deep copy of the NFA."""
        return self.__class__(self.regex.expression)

    @staticmethod
    def _remove_spaces_from_string(string: str) -> str:
        string = string.replace("\n", "").replace(" ", "")
        return string

    @staticmethod
    def _get_regex_symbols(regex: str) -> Set[str]:
        operator = {'+', '&', '*'}
        brackets = {'(', ')', '[', ']', '{', '}'}
        symbols = set()
        for c in regex:
            if c not in operator and c not in brackets:
                symbols.add(c)
        return symbols

    @staticmethod
    def _insert(string: str, index: int, c: str) -> str:
        return string[:index] + c + string[index:]

    def _insert_concatenate_operator(self, regex: str) -> str:
        """insert a concatenate operator's symbol between operands. Example: ab(a) -> a&b&(a)."""

        symbols = self._get_regex_symbols(regex)
        i = 0
        while i < len(regex)-1:

            if regex[i] in symbols and (regex[i+1] in symbols or regex[i+1] == '(' or regex[i+1] == '{' or regex[i+1] == '['):
                regex = self._insert(
                    regex, i+1, '&')

            elif (regex[i] == ')' or regex[i] == '}' or regex[i] == ']') and (regex[i+1] in symbols or regex[i+1] == '(' or regex[i+1] == '{' or regex[i+1] == '['):
                regex = self._insert(
                    regex, i+1, '&')

            elif regex[i] == '*' and (regex[i+1] in symbols or regex[i+1] == '(' or regex[i+1] == '{' or regex[i+1] == '['):
                regex = self._insert(
                    regex, i+1, '&')
            i += 1
        return regex

    def _construct_transitions_table(self) -> None:
        """Construct NFA transitions table of Regex."""
        postfix_regex = self.regex.postfix()
        transitions = {}
        stack = []
        stateNo = 0
        for token in postfix_regex:
            if self.regex.is_operand(token):
                stack.append((str(stateNo), str(stateNo+1)))
                transitions.setdefault(str(stateNo), {}).setdefault(
                    token, set()).add(str(stateNo+1))
                stateNo += 2
            else:
                if self.regex.is_binary_operator(token):
                    op2 = stack[-1]
                    stack.pop()
                    op1 = stack[-1]
                    stack.pop()
                    if(token == '&'):
                        transitions.setdefault(op1[1], {}).setdefault(
                            '$', set()).add(op2[0])
                        stack.append((op1[0], op2[1]))
                    else:
                        transitions.setdefault(str(stateNo), {}).setdefault(
                            '$', set()).add(op1[0])
                        transitions.setdefault(str(stateNo), {}).setdefault(
                            '$', set()).add(op2[0])
                        transitions.setdefault(op1[1], {}).setdefault(
                            '$', set()).add(str(stateNo+1))
                        transitions.setdefault(op2[1], {}).setdefault(
                            '$', set()).add(str(stateNo+1))
                        stack.append((str(stateNo), str(stateNo+1)))
                        stateNo += 2
                else:
                    op1 = stack[-1]
                    stack.pop()
                    transitions.setdefault(str(stateNo), {}).setdefault(
                        '$', set()).add(op1[0])
                    transitions.setdefault(op1[1], {}).setdefault(
                        '$', set()).add(str(stateNo+1))
                    transitions.setdefault(op1[1], {}).setdefault(
                        '$', set()).add(op1[0])
                    transitions.setdefault(str(stateNo), {}).setdefault(
                        '$', set()).add(str(stateNo+1))
                    stack.append((str(stateNo), str(stateNo+1)))
                    stateNo += 2
        transitions[stack[-1][1]] = {}

        self.transitions_table = copy.deepcopy(transitions)
        self.states = sorted(transitions.keys())
        self.symbols = self.regex.get_operands()
        self.symbols.add('$')
        self.start_state = stack[-1][0]
        self.final_state = stack[-1][1]

    def closure(self) -> NFA:
        """Return NFA that accepts the regex repeated zero or more times."""
        return NFA(f"({self.regex.expression})*")

    def union(self, regex: str) -> NFA:
        """
        Return NFA that accepts union of this regex with another regex.
        regex: the regex that will be unioned with the object regex
        regex type: str
        """
        if not isinstance(regex, str):
            raise TypeError(
                f"regex has to be a str. {regex} is {type(regex)}, not str.")
        return NFA(f"({self.regex.expression})+({regex})")

    def concatenate(self, regex: str) -> NFA:
        """
        Return NFA that accepts concatenation of this regex and another regex.
        regex: the regex that will be concatenated with the object regex
        regex type: str
        """
        if not isinstance(regex, str):
            raise TypeError(
                f"regex has to be a str. {regex} is {type(regex)}, not str.")
        return NFA(f"({self.regex.expression})({regex})")

    def state_epsilon_closure(self, state: str) -> Set[str]:
        """
        Return set of reachable states by following zero or more epsilon transitions.
        state: the method start from it(state) and discover all states that reachable from it by following zero or more epsilon transitions
        state type: str
        """
        if not isinstance(state, str):
            raise TypeError(
                f"state has to be a str. {state} is {type(state)}, not str.")
        if state not in self.states:
            raise InvalidStateException(f"the state{state} is not valid")
        states = set()
        stack = [state]
        while stack:
            stack_top = stack.pop()
            if stack_top not in states:
                states.add(stack_top)
                stack.extend(
                    self.transitions_table[stack_top].setdefault('$', set()))
        return states

    def check_input(self, input: str) -> Tuple[bool, set]:
        """
        Return True if the input is accepted by the regex, and last states the input reaches
        input: the string that will be checked, if it is accepted by the regex
        input type: str
        """
        if not isinstance(input, str):
            raise TypeError(
                f"input has to be a str. {input} is {type(input)}, not str.")
                
        current_states = self.state_epsilon_closure(self.start_state)

        for c in input:
            next_states = set()

            for state in current_states:
                next_states.update(
                    self.transitions_table[state].setdefault(c, set()))
            for state in next_states.copy():
                next_states.update(self.state_epsilon_closure(state))
            current_states = next_states

        return self.final_state in current_states, current_states

    def visualize(self, *, filename: str = 'nfa-graph',
                  format: str = 'png',
                  path: str = None,
                  size: Tuple[int, int] = (8, 69),
                  view: bool = False,
                  state_color: str = "#000000",
                  subgroup_states: set = set(),
                  subgroup_color: str = "#A8A8A8",
                  bgcolor: str = "#FFFFFF",
                  arrow_color: str = "#000000",
                  fontcolor: str = "#000000") -> Digraph:
        """
        Return NFA graph.
        filename: name of file of nfa graph
        filename type: str
        path: the path that the file will be saved in
        path type: str
        size: size of graph "states and arrows"
        size type: tuple of size two, and its element type is int
        view: if True the file will be opened 
        view type: bool
        state_color: color of the states
        state_color type: str of hex or color name
        subgroup_states: subgroup to be colored with different color
        subgroup_states type: set
        subgroup_color: color of the subgroup
        subgroup_color type: str of hex or color name
        bgcolor: color of background
        bgcolor type: str of hex or color name
        arrow_color: color of arrow
        arrow_color type: str of hex or color name
        fontcolor: color of font in the graph
        fontcolor type: str of hex or color name
        """

        graph = Digraph('NFA Graph')

        graph.attr(rankdir='LR', size=','.join(
            [str(i) for i in size]), bgcolor=bgcolor)

        graph.node('Initial', shape='point',
                   color=state_color, fontcolor=fontcolor)
        for state in self.states:
            if state == self.final_state and state in subgroup_states:
                graph.node(state, shape='doublecircle',
                           color=state_color, fillcolor=subgroup_color, style='filled', fontcolor=fontcolor)
            elif state == self.final_state:
                graph.node(state, shape='doublecircle',
                           color=state_color, fontcolor=fontcolor)
            elif state in subgroup_states:
                graph.node(state, shape='circle',
                           color=state_color, fillcolor=subgroup_color, style='filled', fontcolor=fontcolor)
            else:
                graph.node(state, shape='circle',
                           color=state_color, fontcolor=fontcolor)

        for stateFrom in self.transitions_table.keys():
            for symbol in self.transitions_table[stateFrom].keys():
                for stateTo in self.transitions_table[stateFrom][symbol]:
                    graph.edge(stateFrom, stateTo,
                               label=symbol, color=arrow_color, fontcolor=fontcolor)
        graph.edge('Initial', self.start_state, color=arrow_color)

        if view:
            graph.render(filename=filename, format=format,
                         directory=path, view=True)
        else:
            graph.render(filename=filename, format=format, directory=path)
        return graph
