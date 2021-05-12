import re
import conllu
import 'token_class.py'

# the conllu library parses the file into sentences and each sentence into tokens; each token is a dictionary with with the following keys:
# id, form, lemma, upos, xpos, feats, head, deprel, deps, misc.

def parse_filter(sentence):
    filtered_sentence = []
    
    for token in sentence:
        if is_deprel(token['deprel']) == False:
            return False
        
            # if the sentence has a token in it with a deprel value which is not in the set of accepted deprels, it is not parsable.

        elif token['deprel'] in no_equivalents['sentence']:
            return False

            # if the sentence has a token in it with a deprel value in the list no_equivalents['sentence'], it is not parsable.
            # deprels in this set are part of UD but deemed unparsable by the engineer.

        elif token['deprel'] in no_equivalents['token']:
            pass

            # if a token has a deprel value in the list no_equivalents['token'], that token is ignored.

        else:
            filtered_sentence.append(token)

            # any token which passes these criteria is appended to the filtered sentence, which is ready to be converted to an f_structure.

    return filtered_sentence

def f_hierarchy(token):
    if token.gf == '*CONJ':
        return 7

    elif token.gf == 'ADJ':
        return 7

    elif token.gf == 'SUBJ':
        return 0

    elif token.gf == 'OBJ':
        return 1
    
    elif re.search(r'^OBJ:', token.gf) != None:
        return 2

    elif re.search(r'^OBL:?', token.gf) != None:
        return 3

    elif token.gf == 'COMP' or token.gf == 'XCOMP':
        return 4

    else:
        return 5

    # the dummy GF '*CONJ' is given special status as the very lowest in the function hierary,
    # to ensure that the coordination with this dependant happens after the rest of the token's GF's value has already been generated.

def nest_order(tokens):
    ordered_tokens = []
    ordered_tokens_waiting_room = []
    ordered_tokens_reception = []
    terminal_dependants = []

    for token in tokens:
        for other_token in tokens:
            if token.id == other_token.head:
                token.dependants.append(other_token)

                # the tokens' .dependants properties are appended.

        token.dependants.sort(key=f_hierarchy)
        
        # the tokens have their dependants sorted according to the functional hierarchy,
        # with a special place for coordinating conjunctions and parataxis at the end (see. f_hierarchy()).
    
    for token in tokens:
        if len(token.dependants) == 0:
            terminal_dependants.append(token)

            # the terminal dependants are listed.
    
    for token in terminal_dependants:
        pred_format(token)

        # the terminal dependants have their preds formatted.

    for token in tokens:
        if token.head == 0:
            matrix_pred = token
    
            # the matrix predicate is found.

    ordered_tokens.append(matrix_pred)

    for dependant in matrix_pred.dependants:
        ordered_tokens_waiting_room.append(dependant)

        # the matrix predicate is in the ordered list. it's dependants are in the waiting room.
    
    while len(ordered_tokens) < len(tokens):
        for token in ordered_tokens_waiting_room:
            for dependant in token.dependants:
                ordered_tokens_reception.append(dependant)

        ordered_tokens = ordered_tokens + ordered_tokens_waiting_room
        ordered_tokens_waiting_room = ordered_tokens_reception
        ordered_tokens_reception = []

        # the matrix predicate's dependants' dependants arrive at reception.
        # the dependants in the waiting room move out of the loop into the ordered_tokens list, and the dependants at reception take their place.
        # the new dependants in the waiting room have their dependants arrive at reception
        # and the process loops until the ordered_tokens list is as long as the original list.
    
    ordered_heads = []

    for token in ordered_tokens:
        if token not in terminal_dependants:
            ordered_heads.append(token)

    ordered_heads.reverse()

    # the ordered_tokens list has the terminal dependants removed and its order is reversed to reflect the nesting order for f_compose().
    # ordered_tokens is now a list of every token which is the head of another token, ordered from the heads of the terminal dependants to the matrix predicate.
    # this order ensures that no token can nest its dependants inside its value until they have had their turn to nest their dependants and so on.

    return ordered_heads

def pred_format(token):
    exception_preds = ['DEF', 'CASE', 'GEN', 'PERS', 'MOOD', 'TENSE', 'NUM', 'ASP', 'COORD', '*COORD', '*CPOUND']

    if token.upos == 'PRON' and token.gf != 'SPEC':
        token.value['PRED'] = 'PRO'

        return

        # if the token is a pronoun and not a specifier, its PRED value must be PRO.

    elif len(token.arguments) != 0 and token.gf not in exception_preds:
        try:
            token_pred = token.value['PRED']

        except:
            token_pred = token.value[0]['PRED']

        open_arg, close_arg = token_pred.split(' ')
        arg_string = ''

        # if the token has arguments and is not an ADJ, open_arg and close_arg are fragments of the original PRED value.
        # the exception is for formatting PRED values inside coordinations.

        for argument in token.arguments:
            arg_string = arg_string + '(' + argument + ')'

        try:
            token.value['PRED'] = open_arg + arg_string + close_arg
            
        except:
            token.value[0]['PRED'] = open_arg + arg_string + close_arg

            # the new PRED value is formatted to include the names of the argument grammatical functions and added.

    else:
        if token.gf not in exception_preds:
            try:
                token.value['PRED'] = token.lemma

            except:
                token.value[0]['PRED'] = token.lemma

        # if the token has no arguments its PRED value is equal to its lemma, unless it is a special PRED value for GFs like DEF or CASE or a pronoun.
    
    # it is presumed that all ADJ and *COORD PREDs will be formatted before they are coordinated, if that is required (see. f_compose());
    # this function is only designed to be called when the ADJ or *COORD has just one item in its list.

# in sum, these four functions are the toolkit for f_compose(), which returns f_structures for sentences in the HDT-UD.
# parse_filter() allows or disallows and trims the sentences for conversion, f_hierarchy orders GFs on the functional hierarchy,
# nest_order calculates the correct order of nesting for the GFs and pred_format edits the values of the PRED GFs to list the arguments of the function or to otherwise be simplified.

def f_compose(sentence):
    f_structure = {}
    tokens = []

    for token in sentence:
        token_object = Token(token)
        token_object.convert()
        tokens.append(token_object)

        # the sentence's tokens are cast as objects of the type above, converted and listed.

    tokens = nest_order(tokens)

    # the tokens list now contains every token which is the head of another token, with a list of their dependants as a property, ordered for composition.

    for token in tokens:
        if token.head == 0:
            matrix_pred = token

            # the matrix predicate is located.

        for dependant in token.dependants:
            key, value = dependant.gf, dependant.value

            if dependant.arg == True:
                token.arguments.append(key)

                # if the dependant token is an argument, its key is added to its head's list of arguments for pred_format().

            if dependant.gf == '*COORD':
                coordination_list = []

                if type(token.value) is dict:
                    coordination_list.append(token.value)
                        
                elif type(token.value) is list:
                    for sub_value in token.value:
                        coordination_list.append(sub_value)

                for sub_value in dependant.value:
                    coordination_list.append(sub_value)

                token.value = coordination_list
                
                # if the dependant is a coordinated conjuntion or parataxis,
                # the value(s) of the token must be placed inside a list with the coordinated conjunction or parataxis.

            elif dependant.gf == 'COORD':
                    token.value[0]['COORD'] = value
                    
                # if the dependant is a COORD, it must be the dependant of a coordinated conjunction and is nested appropriately.
                # this may result in replacing the default COORD function values 'PARATAXIS' and 'LIST' (see. Token.convert_coordinants()).
                
            elif dependant.gf == '*CPOUND':
                compound_token = dependant.value['PRED']

                if compound_token[0] == '-':
                    new_pred = token.lemma + compound_token

                    try:
                        token.value['PRED'] = '{}< >'.format(new_pred)
                        token.form = '{}'.format(new_pred)
                        token.lemma = '{}'.format(new_pred)
                        
                    except:
                        token.value[0]['PRED'] = '{}< >'.format(new_pred)
                        token.form = '{}'.format(new_pred)
                        token.lemma = '{}'.format(new_pred)

                else:
                    new_pred = compound_token + token.lemma

                    try:
                        token.value['PRED'] = '{}< >'.format(new_pred)
                        token.form = '{}'.format(new_pred)
                        token.lemma = '{}'.format(new_pred)
                        
                    except:
                        token.value[0]['PRED'] = '{}< >'.format(new_pred)
                        token.form = '{}'.format(new_pred)
                        token.lemma = '{}'.format(new_pred)

                # if the dependant is part of a compound, is is placed at either the beginning or the end of the token's PRED value string.

            elif dependant.gf == 'ADJ':
                try:
                    if 'ADJ' in token.value.keys():
                        for sub_value in value:
                            token.value['ADJ'].append(sub_value)

                    else:
                        try:
                            token.value[key] = value

                        except:
                            token.value[0][key] = value
                
                except:
                    if 'ADJ' in token.value[0].keys():
                        for sub_value in value:
                            token.value['ADJ'].append(sub_value)

                    else:
                        try:
                            token.value[key] = value

                        except:
                            token.value[0][key] = value

                # if the dependant's GF is an ADJ, a check is performed to see if an ADJ function is already nested inside the token's value.
                # if there is one, the new ADJ value(s) is (are) appended to the original ADJ's list. if there isn't, the dependant's key and value are nested inside the token's value.
            
            else:
                try:
                    token.value[key] = value

                except:
                    token.value[0][key] = value
                            
                # if the dependant is none of the above (if it is simple),
                # the dependant's key and value are nested inside the token's value (the exception is for nesting inside coordinated values as above).

        pred_format(token)

        # the pred value of the token is formatted to list its arguments if it has any, and to be simplified if it does not.

    key, value = matrix_pred.gf, matrix_pred.value
    f_structure[key] = value

    # every token's conversion to a GF is nested inside the value of its head, and the matrix predicate is nested inside the empty f_structure.
    # because of nest_order(), no GF can be left out of this composition.

    return f_structure

with open('test_compounds.conllu', 'r') as hdt_ud_1to10000A_102001to112000B:
    parse = conllu.parse(hdt_ud_1to10000A_102001to112000B.read())
    
    for sentence in parse:
        filtered_sentence = parse_filter(sentence)

        if filtered_sentence == False:
            pass

        # if the sentence is returned by parse_filter, it has no punctuation, particles or markers, and is ready to be converted into an f-structure.

        f_structure = f_compose(filtered_sentence)
        print(f_structure)