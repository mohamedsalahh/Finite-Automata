# Finite-Automata
Finite state machine simultor for regular expression.

# Requirements
- [Algebraic-Expression-Parser](https://github.com/mohamedsalahh/Algebraic-Expression-Parser)

```
pip install Algebraic-Expression-Parser
```

## NFA
#### Importing
```python
from FiniteAutomata import NFA
```

```python
nfa = NFA('(1+0)*0')
```

```python
print(nfa)
```
```text
< Symbols: {'$', '1', '0'}
  States: ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']
  Transitions Table: {'0': {'1': {'1'}}, '2': {'0': {'3'}}, '4': {'$': {'2', '0'}}, '1': {'$': {'5'}}, '3': {'$': {'5'}}, '6': {'$': {'7', '4'}}, '5':  {'$': {'7', '4'}}, '8': {'0': {'9'}}, '7': {'$': {'8'}}, '9': {}}
  Start State: 6
  Final State: 9 >
```

```python
print(nfa.check_string('10100'))
```
```text
(True, {'2', '7', '8', '4', '5', '9', '3', '0'})
```

```python
print(nfa.check_string('101001'))
```
```text
(False, {'2', '7', '8', '4', '5', '1', '0'})
```

```python
nfa.visualize(state_color='#B5B5B5', bgcolor='#0d1017', fontcolor='#B5B5B5', arrow_color='#B5B5B5')
```
![](https://github.com/mohamedsalahh/Finite-Automata/blob/main/nfa-graph.png "NFA")

```python
states = nfa.check_string('10100')[1]
nfa.visualize(state_color='#B5B5B5', bgcolor='#0d1017', fontcolor='#B5B5B5', arrow_color='#B5B5B5', subgroup_states=states, subgroup_color='#25282e')
```
![](https://github.com/mohamedsalahh/Finite-Automata/blob/main/nfa-graph1.png "NFA")

## DFA
#### Importing
```python
from FiniteAutomata import DFA
```

```python
dfa = DFA(regex='(1+0)*0')
```

```python
print(dfa)
```
```text
< Symbols: {'1', '0'}
  States: ['0', '1', '2']
  Transitions Table: {'2': {'0': '1', '1': '0'}, '1': {'0': '1', '1': '0'}, '0': {'0': '1', '1': '0'}}
  Start State: 2
  Final States: {'1'} >
```

```python
print(dfa.check_string('10100'))
```
```text
(True, '1')
```

```python
print(dfa.check_string('101001'))
```
```text
(False, '0')
```

```python
dfa.visualize(state_color='#B5B5B5', bgcolor='#0d1017', fontcolor='#B5B5B5', arrow_color='#B5B5B5')
```
![](https://github.com/mohamedsalahh/Finite-Automata/blob/main/dfa-graph.png "DFA")

```python
states = set(dfa.check_string('10100')[1])
dfa.visualize(state_color='#B5B5B5', bgcolor='#0d1017', fontcolor='#B5B5B5', arrow_color='#B5B5B5', subgroup_states=states, subgroup_color='#25282e')
```
![](https://github.com/mohamedsalahh/Finite-Automata/blob/main/dfa-graph1.png "DFA")
