import streamlit as st
import re

def remove_left_recursion(grammar):
    store = {}
    for non_terminal in grammar:
        alpha_rules = []
        beta_rules = []
        all_rhs = grammar[non_terminal]
        for sub_rhs in all_rhs:
            if sub_rhs[0] == non_terminal:
                alpha_rules.append(sub_rhs[1:])
            else:
                beta_rules.append(sub_rhs)

        if len(alpha_rules) != 0:
            non_terminal_prime = non_terminal + "'"
            while non_terminal_prime in grammar or non_terminal_prime in store:
                non_terminal_prime += "'"

            for b in range(len(beta_rules)):
                beta_rules[b] = beta_rules[b] + [non_terminal_prime]

            grammar[non_terminal] = beta_rules

            for a in range(len(alpha_rules)):
                alpha_rules[a] = alpha_rules[a] + [non_terminal_prime]

            alpha_rules.append(['#'])
            store[non_terminal_prime] = alpha_rules

    for left in store:
        if left in grammar:
            grammar[left].extend(store[left])
        else:
            grammar[left] = store[left]

    return grammar


def left_factoring(grammar):
    store = {}
    for lhs in grammar:
        all_rhs = grammar[lhs]
        temp = dict()
        for sub_rhs in all_rhs:
            if sub_rhs[0] not in list(temp.keys()):
                temp[sub_rhs[0]] = [sub_rhs]
            else:
                temp[sub_rhs[0]].append(sub_rhs)
        new_rule = []
        tempo_dict = {}
        for term_key in temp:
            all_starting_with_term_key = temp[term_key]
            if len(all_starting_with_term_key) > 1:
                lhs_ = lhs + "'"
                while lhs_ in grammar.keys() or lhs_ in tempo_dict.keys():
                    lhs_ += "'"
                new_rule.append([term_key, lhs_])
                ex_rules = []
                for g in temp[term_key]:
                    ex_rules.append(g[1:])
                tempo_dict[lhs_] = ex_rules
            else:
                new_rule.append(all_starting_with_term_key[0])
        store[lhs] = new_rule
        for key in tempo_dict:
            store[key] = tempo_dict[key]
    return store

def calculate_first(grammar):
    first = {}
    terminals = set()
    non_terminals = set(grammar.keys())

    for nt in non_terminals:
        first[nt] = set()

    for nt, productions in grammar.items():
        for production in productions:
            symbol = production[0]

            if symbol in non_terminals:
                first[nt].update(first[symbol])

                i = 1
                while symbol in non_terminals and '#' in first[symbol] and i < len(production):
                    symbol = production[i]
                    first[nt].update(first[symbol] - {'#'})
                    i += 1

            first[nt].add(symbol)

            if symbol not in non_terminals and symbol != '#':
                terminals.add(symbol)


            if symbol == '#':
                first[nt].add(symbol)  # Include '#' in the first set

    # Replace nonterminals with their first sets
    for nt, symbols in first.items():
        new_symbols = set()
        for symbol in symbols:
            if symbol in non_terminals:
                new_symbols.update(first[symbol])
            else:
                new_symbols.add(symbol)
        first[nt] = new_symbols

    return first, terminals




def calculate_first_set(grammar):
    first_set = {}
    non_terminals = set(grammar.keys())

    for nt in non_terminals:
        first_set[nt] = set()

    changed = True

    while changed:
        changed = False

        for nt, productions in grammar.items():
            for production in productions:
                symbols = production[0][0]

                for symbol in symbols:
                    if symbol in non_terminals:
                        if '#' not in first_set[symbol]:
                            first_set[nt].update(first_set[symbol])
                            break
                        else:
                            first_set[nt].update(first_set[symbol] - {'#'})
                    else:
                        first_set[nt].add(symbol)
                        break
                else:
                    if '#' not in first_set[nt]:
                        first_set[nt].add('#')
                        changed = True

    return first_set



def calculate_follow(grammar, first_set, start_symbol):
    follow_set = {}
    for nt in grammar.keys():
        follow_set[nt] = set()

    follow_set[start_symbol].add('$')

    while True:
        updated = False
        for nt, productions in grammar.items():
            for production in productions:
                production_follow = follow_set[nt]
                for symbol in reversed(production):
                    if symbol in grammar:
                        old_size = len(follow_set[symbol])
                        follow_set[symbol].update(production_follow)
                        if len(follow_set[symbol]) != old_size:
                            updated = True

                        if '#' in first_set[symbol]:
                            production_follow = production_follow.union(first_set[symbol] - {'#'})
                        else:
                            production_follow = first_set[symbol]
                    else:
                        production_follow = set(symbol)  # Treat terminals as their own follow set
        if not updated:
            break

    return follow_set

def generate_parsing_table(grammar, first_set, follow_set):
    parsing_table = {}

    for non_terminal, productions in grammar.items():
        parsing_table[non_terminal] = {}

        for production in productions:
            first_of_production = calculate_first_for_production(production, first_set)

            for symbol in first_of_production - {'#'}:
                if symbol in parsing_table[non_terminal]:
                    raise ValueError(f"Grammar is not LL(1) at {non_terminal} for symbol {symbol}")
                parsing_table[non_terminal][symbol] = production

            if '#' in first_of_production:
                for symbol in follow_set[non_terminal]:
                    if symbol in parsing_table[non_terminal]:
                        raise ValueError(f"Grammar is not LL(1) at {non_terminal} for symbol {symbol}")
                    parsing_table[non_terminal][symbol] = production

    return parsing_table


def calculate_first_for_production(production, first_set):
    first_for_production = set()
    
    for symbol in production:
        if symbol in first_set:
            first_for_production.update(first_set[symbol])
            if '#' not in first_set[symbol]:
                break
        else:
            first_for_production.add(symbol)
            break
    else:
        first_for_production.add('#')
    
    return first_for_production

def validateStringUsingStackBuffer(parsing_table, input_string):
    result = ""
    stack = ["S", "$"]
    buffer = ["$"] + list(input_string)

    result += f"\n{'Buffer':>20} {'Stack':>20} {'Action':>20}\n"
    result += f"{' '.join(buffer[1:][::-1]):>20} {' '.join(stack):>20}\n"

    while True:
        if stack == ["$"] and buffer == ["$"]:
            result += f"{'$':>20} {'$':>20} {'Valid':>20}\n\nValid String!"
            break
        elif stack[0] == "#":
            result += f"{' '.join(buffer[1:][::-1]):>20} {' '.join(stack):>20} {f'Removed: #':>20}\n"
            stack = stack[1:]
        elif stack[0] in parsing_table:
            x = stack[0]
            y = buffer[-1]
            if y in parsing_table[x]:
                entry = parsing_table[x][y]
                result += f"{' '.join(buffer[1:][::-1]):>20} {' '.join(stack):>20} {f'T[{x}][{y}] = {entry}':>20}\n"
                stack = list(entry) + stack[1:]
            else:
                result += f"\nInvalid String! No rule at Table[{x}][{y}]."
                break
        else:
            if stack[0] == buffer[-1]:
                result += f"{' '.join(buffer[1:][::-1]):>20} {' '.join(stack):>20} {f'Matched:{stack[0]}':>20}\n"
                buffer = buffer[:-1]
                stack = stack[1:]
            else:
                result += "\nInvalid String! Unmatched terminal symbols"
                break

    return result


    
import pandas as pd

def main():
    st.title("Left Recursion, Left Factoring, and First Set")

    # Input grammar
    st.header("Input Grammar")
    st.write("Enter the grammar rules in the format 'A -> B C | D E'")
    st.write("Use '#' to represent epsilon/empty production")

    rules = st.text_area("Grammar Rules")
    input_string = st.text_input("Enter the input string:",key="input_string")
    # Process input
    if st.button("Remove Left Recursion"):
        # Parse input grammar
        grammar = {}
        rule_lines = rules.strip().split("\n")
        for rule_line in rule_lines:
            rule_parts = rule_line.split("->")
            non_terminal = rule_parts[0].strip()
            production = rule_parts[1].strip().split("|")
            grammar[non_terminal] = [p.strip().split(" ") for p in production]
    # Add new start symbol 'G'
        new_start_symbol = 'G'
        while new_start_symbol in grammar:
            new_start_symbol += "'"

        grammar[new_start_symbol] = [[list(grammar.keys())[0], '$']]

        # Apply remove_left_recursion function
        result = remove_left_recursion(grammar)
        st.header("Result - After Removing Left Recursion")
        for non_terminal, productions in result.items():
            for production in productions:
                production_str = " ".join(str(p) for p in production)
                st.write(f"{non_terminal} -> {production_str}")



    if st.button("Apply Left Factoring"):
        # Parse input grammar
        grammar = {}
        rule_lines = rules.strip().split("\n")
        for rule_line in rule_lines:
            rule_parts = rule_line.split("->")
            non_terminal = rule_parts[0].strip()
            production = rule_parts[1].strip().split("|")
            grammar[non_terminal] = [p.strip().split(" ") for p in production]
        result = remove_left_recursion(grammar)
        # Apply left_factoring function
        new_start_symbol = 'G'
        while new_start_symbol in grammar:
            new_start_symbol += "'"

        grammar[new_start_symbol] = [[list(grammar.keys())[0], '$']]
        result = left_factoring(result)        
        st.header("Result - After Applying Left Factoring")
        for non_terminal, productions in result.items():
            for production in productions:
                production_str = " ".join(str(p) for p in production)
                st.write(f"{non_terminal} -> {production_str}")

    if st.button("Calculate First Set"):
        # Parse input grammar
        grammar = {}
        rule_lines = rules.strip().split("\n")
        for rule_line in rule_lines:
            rule_parts = rule_line.split("->")
            non_terminal = rule_parts[0].strip()
            production = rule_parts[1].strip().split("|")
            grammar[non_terminal] = [p.strip().split(" ") for p in production]
        new_start_symbol = 'G'
        while new_start_symbol in grammar:
            new_start_symbol += "'"

        grammar[new_start_symbol] = [[list(grammar.keys())[0], '$']]
        # Apply remove_left_recursion function
        result = remove_left_recursion(grammar)

        # Apply left_factoring function
        result = left_factoring(result)

        # Calculate First set
        first_set, terminals = calculate_first(result)

        st.header("Result - First Set")
        for nt, first in first_set.items():
            if any(symbol in first_set for symbol in first):
                new_first = set()
                for symbol in first:
                    if symbol in first_set:
                        new_first.update(first_set[symbol])
                    else:
                        new_first.add(symbol)
                        

                first = new_first
             
            first_str = ", ".join(str(f) for f in first)
            st.write(f"First({nt}) = {{{first_str}}}")
            

    
    if st.button("Calculate Follow Set"):
        # Parse input grammar
        grammar = {}
        rule_lines = rules.strip().split("\n")
        start_symbol = 'G'
        for rule_line in rule_lines:
            rule_parts = rule_line.split("->")
            non_terminal = rule_parts[0].strip()
            production = rule_parts[1].strip().split("|")
            grammar[non_terminal] = [p.strip().split(" ") for p in production]
        new_start_symbol = 'G'
        while new_start_symbol in grammar:
            new_start_symbol += "'"

        grammar[new_start_symbol] = [[list(grammar.keys())[0], '$']]
        # Apply remove_left_recursion function
        result = remove_left_recursion(grammar)

        # Apply left_factoring function
        result = left_factoring(result)

        # Calculate First set
        first_set, terminals = calculate_first(result)

        # Calculate Follow set
        follow_set = calculate_follow(result, first_set, start_symbol)

        st.header("Result - Follow Set")
        for nt, follow in follow_set.items():
            follow_str = ", ".join(str(f) for f in follow)
            st.write(f"Follow({nt}) = {{{follow_str}}}")
            
    if st.button("Generate Parsing Table"):
    # Parse input grammar
        grammar = {}
        rule_lines = rules.strip().split("\n")

        for rule_line in rule_lines:
            rule_parts = rule_line.split("->")
            non_terminal = rule_parts[0].strip()
            production = rule_parts[1].strip().split("|")
            grammar[non_terminal] = [p.strip().split(" ") for p in production]
        new_start_symbol = 'G'
        while new_start_symbol in grammar:
            new_start_symbol += "'"

        grammar[new_start_symbol] = [[list(grammar.keys())[0], '$']]
    # Apply remove_left_recursion function
        result = remove_left_recursion(grammar)

    # Apply left_factoring function
        result = left_factoring(result)

    # Calculate First set
        first_set, _ = calculate_first(result)

    # Calculate Follow set
        start_symbol = list(result.keys())[0]
        follow_set = calculate_follow(result, first_set, start_symbol)

    # Generate parsing table
        parsing_table = generate_parsing_table(result, first_set, follow_set)
        all_symbols = set(symbol for productions in result.values() for production in productions for symbol in production)

        all_symbols1 = [symbol for symbol in all_symbols if symbol not in result.keys() or symbol == "$"]
        st.header("Parsing Table")
        data = {symbol: [parsing_table.get(non_terminal, {}).get(symbol, "") for non_terminal, productions in result.items()] for symbol in all_symbols1}
        df = pd.DataFrame(data, index=list(result.keys()))  

        st.write(all_symbols)
        for non_terminal, productions in result.items():
            for production in productions:
                production_str = " ".join(production)
                for symbol in all_symbols1:
                    if df.loc[non_terminal, symbol] == production:
                    
                        df.loc[non_terminal, symbol] = f"{non_terminal} -> {production_str}"
        for symbol in first_set["G"]:
            if symbol == first_set["G"]:
                df.loc["G", symbol] = "G -> S$"
        st.dataframe(df)
   

        
        
        duplicate_entries = False
        for column in df.columns:
            unique_entries = df[column].unique()
            unique_entries = [str(entry) for entry in unique_entries]  # Convert entries to strings
            if len(set(unique_entries)) > 1:
                duplicate_entries = True
                break

        if duplicate_entries== False:
            st.write("Grammar is not LL(1).")
        else:
            st.write("Grammar is LL(1).")

        

        input_string = input_string[::-1]
        final = validateStringUsingStackBuffer(parsing_table, input_string)
        st.text(final)
        
      


    


# Run the app
if __name__ == "__main__":
    main()
