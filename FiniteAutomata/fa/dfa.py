import copy
from os import stat
from typing import Tuple, TypeVar
from AlgebraicExpressionParser import Expression
from FiniteAutomata.exceptions.Exceptions import *
from FiniteAutomata.fa.nfa import NFA
from graphviz import Digraph

DFA = TypeVar('DFA')


class DFA:
    def __init__(self, *, regex: str = None, nfa: NFA = None) -> None:

        if nfa:
            self.nfa = nfa.copy()
        elif regex:
            self.regex = regex
        else:
            raise DFAInvalidArgumentsException(
                "DFA class should be given regex or NFA.")

    @property
    def nfa(self) -> NFA:
        return self._nfa

    @nfa.setter
    def nfa(self, nfa: NFA) -> None:
        self._nfa = nfa
        self._convert_NFA_To_DFA()
        self._shrink_states_names()

    @property
    def regex(self) -> Expression:
        return self.nfa.regex

    @regex.setter
    def regex(self, regex: str) -> None:
        self.nfa = NFA(regex)

    def __str__(self) -> str:
        return f"< Symbols: {self.symbols}\n  States: {self.states}\n  Transitions Table: {self.transitions_table}\n  Start State: {self.start_state}\n  Final States: {self.final_states} >"

    def __repr__(self) -> str:
        return f"DFA('regex = {self.regex.expression}')"

    def __iter__(self):
        for state, transitions in self.transitions_table.items():
            yield (state, transitions)

    def copy(self) -> DFA:
        """Create a deep copy of the DFA."""
        return self.__class__(nfa = self.nfa)

    def _convert_NFA_To_DFA(self) -> None:
        """Convert NFA transitions to DFA transitions"""

        DFA_Transitions = {}
        DFA_States = []
        has_deadState = False
        symbols = self.regex.get_operands()
        symbols.discard('$')

        states_epsilon_closure = {}
        for state in self.nfa.transitions_table.keys():
            states_epsilon_closure[state] = self.nfa.state_epsilon_closure(
                state)

        DFA_States.append(sorted(states_epsilon_closure[self.nfa.start_state]))
        self.start_state = ','.join(
            sorted(states_epsilon_closure[self.nfa.start_state]))
        self.final_states = set()

        for DfaStateFrom in DFA_States:
            DfaStateFrom_Str = ','.join(sorted(DfaStateFrom))
            DFA_Transitions[DfaStateFrom_Str] = {}

            if self.nfa.final_state in DfaStateFrom:
                self.final_states.add(DfaStateFrom_Str)

            for symbol in sorted(symbols):
                DfaStateTo = set()
                for stateFrom in DfaStateFrom:
                    for stateTo in self.nfa.transitions_table[stateFrom].setdefault(symbol, set()):
                        DfaStateTo.add(stateTo)
                        DfaStateTo.update(states_epsilon_closure[stateTo])

                DfaStateTo_Str = ','.join(sorted(DfaStateTo))
                DFA_Transitions[DfaStateFrom_Str][symbol] = DfaStateTo_Str

                if DfaStateTo_Str == '':
                    has_deadState = True
                    DFA_Transitions[DfaStateFrom_Str][symbol] = "Dead State"

                if sorted(DfaStateTo) not in DFA_States and DfaStateTo:
                    DFA_States.append(sorted(DfaStateTo))

        if has_deadState:
            DFA_Transitions["Dead State"] = {}
            for symbol in sorted(symbols):
                DFA_Transitions["Dead State"][symbol] = "Dead State"

        self.transitions_table = copy.deepcopy(DFA_Transitions)
        self.states = sorted(DFA_Transitions.keys())
        self.symbols = self.regex.get_operands()

    def minimize(self) -> DFA:
        """Minimize the DFA states using Hopcroft's algorithm"""
        equivalence_classes = []
        equivalence_classes.append(copy.copy(self.final_states))
        equivalence_classes.append(set(self.states).difference(self.final_states))

        while True:    
            counter = 0
            state_class = {}
            for Class in equivalence_classes:
                for state in Class:
                    state_class[state] = counter
                counter += 1
                
            prev_equivalence_classes = copy.deepcopy(equivalence_classes)
            next_equivalence_classes = []
            for Class in equivalence_classes:
                while Class:
                    curr_state = Class.pop()
                    next_class = {curr_state}
                    for state in sorted(Class):
                        flag = True
                        for symbol in self.symbols:
                            if state_class[self.transitions_table[state][symbol]] != state_class[self.transitions_table[curr_state][symbol]]:
                                flag = False
                                break
                        if flag:
                            next_class.add(state)
                            Class.remove(state)
                    next_equivalence_classes.append(next_class)
            equivalence_classes = next_equivalence_classes
    
            if prev_equivalence_classes == next_equivalence_classes:
                break  

        new_transitions_table = {}
        for class_from in equivalence_classes:
            new_transitions_table[','.join(sorted(class_from))] = {}
            for symbol in self.symbols:
                state_to = self.transitions_table[list(class_from)[0]][symbol]
                for class_to in equivalence_classes:
                    if state_to in class_to:
                        new_transitions_table[','.join(sorted(class_from))][symbol] = ','.join(sorted(class_to))
                        break

        new_dfa = self.copy()
        new_dfa.transitions_table = copy.deepcopy(new_transitions_table)
        new_dfa.states = sorted(new_transitions_table.keys())

        for Class in equivalence_classes:
            if new_dfa.start_state in Class:
                new_dfa.start_state = ','.join(sorted(Class))
                break
        final_states_temp = set()
        for Class in equivalence_classes:
            for state in new_dfa.final_states:
                if state in Class:
                    final_states_temp.add(','.join(sorted(Class)))
        new_dfa.final_states = copy.copy(final_states_temp)
        new_dfa._shrink_states_names()

        return new_dfa

    def _shrink_states_names(self) -> None:
        "Shrink DFA states names that formed from converting NFA to DFA or merging states"
        mapping = {}
        for num, state in enumerate(self.states):
            mapping[state] = str(num)

        for stateFrom in copy.deepcopy(self.transitions_table):
            for symbol in copy.deepcopy(self.transitions_table[stateFrom]):
                self.transitions_table[stateFrom][symbol] = mapping[self.transitions_table[stateFrom][symbol]]
            self.transitions_table[mapping[stateFrom]
                                   ] = self.transitions_table.pop(stateFrom)

        self.states = sorted(self.transitions_table.keys())
        self.start_state = mapping[self.start_state]

        for state in self.final_states.copy():
            self.final_states.remove(state)
            self.final_states.add(mapping[state])

    def check_input(self, input: str) -> Tuple[bool, str]:
        """
        Return True if the input is accepted by the regex, and last state the input reaches.
        input: the string that will be checked, if it is accepted by the regex
        input type: str
        """
        if not isinstance(input, str):
            raise TypeError(
                f"input has to be a str. {input} is {type(input)}, not str.")
        current_state = self.start_state
        for c in input:
            current_state = self.transitions_table[current_state][c]

        return current_state in self.final_states, current_state

    def closure(self) -> DFA:
        """Return DFA that accepts the regex repeated zero or more times"""
        return DFA(nfa=self.nfa.closure())

    def union(self, regex: str) -> DFA:
        """
        Return DFA that accepts union of this regex with another regex.
        regex: the regex that will be unioned with the object regex
        regex type: str
        """
        return DFA(nfa=self.nfa.union(regex))

    def concatenate(self, regex: str) -> DFA:
        """
        Return DFA that accepts concatenation of this regex and another regex.
        regex: the regex that will be concatenated with the object regex
        regex type: str
        """
        return DFA(nfa=self.nfa.concatenate(regex))

    def visualize(self, *, filename: str = 'dfa-graph',
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

        graph = Digraph('DFA Graph')

        graph.attr(rankdir='LR', size=','.join(
            [str(i) for i in size]), bgcolor=bgcolor)

        graph.node('Initial', shape='point',
                   color=state_color, fontcolor=fontcolor)
        for state in self.states:
            if state in self.final_states and state in subgroup_states:
                graph.node(state, shape='doublecircle',
                           color=state_color, fillcolor=subgroup_color, style='filled', fontcolor=fontcolor)
            elif state in self.final_states:
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
                graph.edge(stateFrom, self.transitions_table[stateFrom][symbol],
                           label=symbol, color=arrow_color, fontcolor=fontcolor)
        graph.edge('Initial', self.start_state, color=arrow_color)

        if view:
            graph.render(filename=filename, format=format,
                         directory=path, view=True)
        else:
            graph.render(filename=filename, format=format, directory=path)
        return graph
