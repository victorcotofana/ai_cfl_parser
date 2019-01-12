
def read_from_file(file_name):
    with open(file_name) as fd:
        messages = fd.read().replace('\n', '').split('.')
    messages = list(map(lambda message: message.strip(), messages))
    # print(messages[:-1])
    return messages[:-1]


def print_dict(dictionary):
    if isinstance(dictionary, bool):
        print('No way')
    else:
        for key in dictionary.keys():
            print('\'' + key + '\':', dictionary[key])


def generate_simple_grammar(messages):
    nonterminal_count = 0
    new_grammar = {}
    for message in messages:
        for index, word in enumerate(message.split(' ')):
            # print(index, word)
            current_nonterminal = '$' + str(nonterminal_count)
            if index is 0:  # primul cuvant din mesaj mereu va incepe din primul neterminal
                nonterminal_count += 1
                next_nonterminal = '$' + str(nonterminal_count)
                if new_grammar.get('$0') is None:
                    new_grammar['$0'] = [[word, next_nonterminal]]
                else:
                    new_grammar['$0'] += [[word, next_nonterminal]]
            else:
                if new_grammar.get(current_nonterminal) is None:
                    nonterminal_count += 1
                    next_nonterminal = '$' + str(nonterminal_count)
                    if index is (len(message.split(' ')) - 1):
                        new_grammar[current_nonterminal] = [[word, None]]
                    else:
                        new_grammar[current_nonterminal] = [[word, next_nonterminal]]
    # print_dict(grammar)
    return new_grammar


def grammar_compression(grammar, no_max_rules):
    unique_terminals_grammar = unique_terminals(grammar)
    return combine_terminals(unique_terminals_grammar, no_max_rules)


def unique_terminals(grammar_to_change):
    none_keys = []

    # parcurgem nonterminalii de jos in sus, adaugand la regulile de sus
    for nonterminal_to_delete in list(reversed(list(grammar_to_change))):
        if grammar_to_change[nonterminal_to_delete] is None:
            continue
        current_terminal = grammar_to_change[nonterminal_to_delete][0][0]
        for nonterminal_to_add in grammar_to_change:
            if grammar_to_change[nonterminal_to_add] is None:
                continue

            # verificam daca nu e aceeasi regula si ca terminalul e la fel
            if nonterminal_to_add is not nonterminal_to_delete \
                    and current_terminal == grammar_to_change[nonterminal_to_add][0][0]:
                # tre de verificat daca regula nu exista deja
                for new_rules in grammar_to_change[nonterminal_to_delete]:
                    if new_rules not in grammar_to_change[nonterminal_to_add]:
                        grammar_to_change[nonterminal_to_add] = grammar_to_change[nonterminal_to_add] + [new_rules]
                grammar_to_change[nonterminal_to_delete] = None
                none_keys.append(nonterminal_to_delete)

                # tre de redirectionat nonterminal_to_delete catre nonterminal_to_add
                for nonterminal_to_change in grammar_to_change:
                    if grammar_to_change[nonterminal_to_change] is None:
                        continue

                    if len(grammar_to_change[nonterminal_to_change][0]) > 1 \
                            and grammar_to_change[nonterminal_to_change][0][1] == nonterminal_to_delete:
                        grammar_to_change[nonterminal_to_change][0].pop()
                        grammar_to_change[nonterminal_to_change][0].append(nonterminal_to_add)

    # stergem toate cheile None
    for none_key in none_keys:
        del grammar_to_change[none_key]
    # print_dict(grammar_to_change)

    return grammar_to_change


def combine_terminals(grammar, no_max_rules):
    one_rule_modified = False
    # modificam one rule at a time
    while count_rules(grammar) > no_max_rules:
        # for i in range(0, 9): # for test purposes
        # incepem de sus
        for first_nonterminal in grammar:
            for rules in grammar[first_nonterminal]:
                if rules is None or len(rules) is 1:
                    continue
                nonterminal_to_check = rules[1]
                if nonterminal_to_check is None:
                    continue
                is_terminal_used = False
                # tre de verificat ca alte reguli nu au deja neterminalul pe care vrem sa il merge-uim
                for second_nonterminal in grammar:
                    if second_nonterminal == first_nonterminal:
                        continue
                    for second_rules in grammar[second_nonterminal]:
                        if second_rules is not None and len(second_rules) > 1 \
                                and second_rules[1] == nonterminal_to_check:
                            is_terminal_used = True
                            break
                    if is_terminal_used:
                        break

                if not is_terminal_used:
                    merge_rules = grammar[nonterminal_to_check]

                    if len(merge_rules) is 1:
                        rules[0] = rules[0] + ' ' + merge_rules[0][0]
                        rules[1] = merge_rules[0][1]
                        one_rule_modified = True
                        grammar[nonterminal_to_check] = [None]
                        break
                    else:
                        new_rules = []
                        for merge_rule in merge_rules:
                            new_terminal = rules[0] + ' ' + merge_rule[0]
                            new_nonterminal = merge_rule[1]
                            new_rules.append([new_terminal, new_nonterminal])
                        grammar[first_nonterminal] = new_rules
                        one_rule_modified = True
                    grammar[nonterminal_to_check] = [None]
                # print_dict(grammar)
                if one_rule_modified is True:
                    break
            if one_rule_modified is True:
                break
        grammar = clean_grammar(grammar)
        if one_rule_modified is False:
            return False
        one_rule_modified = False
    # print_dict(grammar)
    return grammar


def count_rules(grammar):
    no_rules = 0
    for nonterminal in grammar:
        no_rules += len(grammar[nonterminal])
    return no_rules


def clean_grammar(grammar):
    empty_rules_keys = []
    for nonterminal in grammar:
        if len(grammar[nonterminal]) is 1 and grammar[nonterminal][0] is None:
            empty_rules_keys.append(nonterminal)
    for delete_key in empty_rules_keys:
        del grammar[delete_key]
    return grammar


def get_best_grammar(messages, no_max_rules):
    simple_grammar = generate_simple_grammar(messages)
    best_grammar = grammar_compression(simple_grammar, no_max_rules)
    if best_grammar is False:
        return get_best_grammar(messages[:-1], no_max_rules)
    else:
        return best_grammar


input_messages = read_from_file('input.txt')
# print_dict(get_best_grammar(input_messages, 10))  # full grammar
print_dict(get_best_grammar(input_messages, 3))  # minimal grammar
