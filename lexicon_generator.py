import re

# Lexicon that can be added to Attempto Editor
lexicon = []
# list that links the IDP voc to the corresponding Attempto words
link_IDP_Attempto = []
# function dummy
functions_IDP = []


# read types from annotated IDP voc and transform to nouns in Attempto
def generate_types(idp_voc):
    pattern_type = re.compile(r'(type)\s?([A-Za-z]+)//([A-Za-z]+),\s?([A-Za-z]+)')
    matches = pattern_type.finditer(idp_voc)
    for i in matches:
        link_IDP_Attempto.append((i[3], i[2]))
        functions_IDP.append((i[3], False))
        lexicon.append("noun_sg({0},{0},neutr).\nnoun_pl({1},{0},neutr).\n".format(i[3], i[4]))


# Read constructed types and generate proper names and nouns
def generate_constructor_types(idp_voc):
    pattern_constr_type = re.compile(
        r'(type)\s?([A-Za-z]*.+\)?) constructed from \{([^}]*)}\s?//\s?([A-Za-z]+),\s?([A-Za-z]+),\s?\{([^}]*)}')
    matches = pattern_constr_type.finditer(idp_voc)
    for i in matches:
        link_IDP_Attempto.append((i[4], i[2]))
        functions_IDP.append((i[4], False))
        lexicon.append("noun_sg({0},{0},neutr).\nnoun_pl({1},{0},neutr).\n".format(i[4], i[5]))
        constructed = i[3].split(',')
        genders = i[6].split(',')
        for j in range(0, len(constructed)):
            lexicon.append("pn_sg('{0}','{0}',{1}).\n".format(constructed[j], genders[j]))


#adds function to the dictionaries and sets function_dummy true, also adds quotation marks if the word is hyphenated (required by ACE)
def add_to_dictionary_function_true(annotated_function):
    if '-' in annotated_function[4]:
        link_IDP_Attempto.append(("'{0}'".format(annotated_function[4]), annotated_function[1]))
        functions_IDP.append(("'{0}'".format(annotated_function[4]), True))
    else:
        link_IDP_Attempto.append((annotated_function[4], annotated_function[1]))
        functions_IDP.append((annotated_function[4], True))

#adds relations to the dictionaries
def add_to_dictionary_function_false(annotated_relation):
    if '-' in annotated_relation[4]:
        link_IDP_Attempto.append(("'{0}'".format(annotated_relation[4]), annotated_relation[1]))
        functions_IDP.append(("'{0}'".format(annotated_relation[4]), False))
    else:
        link_IDP_Attempto.append((annotated_relation[4], annotated_relation[1]))
        functions_IDP.append((annotated_relation[4], False))


# adds the verb entries to the lexicon
def generate_verb_entries(annotations):
    if annotations[6]:
        if '-' in annotations[4]:
            lexicon.append(
                "tv_finsg('{1}','{0}').\ntv_infpl('{0}','{0}').\ntv_pp('{2}','{0}').\n".format(annotations[4],
                                                                                               annotations[5],
                                                                                               annotations[6]))
        else:
            lexicon.append(
                "tv_finsg({1},{0}).\ntv_infpl({0},{0}).\ntv_pp({2},{0}).\n".format(annotations[4], annotations[5],
                                                                                   annotations[6]))
    else:
        if '-' in annotations[4]:
            lexicon.append("iv_finsg('{1}','{0}').\niv_infpl('{0}','{0}').\n".format(annotations[4], annotations[5]))
        else:
            lexicon.append("iv_finsg({1},{0}).\niv_infpl({0},{0}).\n".format(annotations[4], annotations[5]))

# detects verb entries
def generate_verbs(idp_voc):
    pattern_verb_relation = re.compile(
        r'([a-zA-Z]+)\(+([a-zA-Z]+),*([a-zA-Z]*)\)\s?//\s?verb,\s?(\'?[a-z]+-?[a-z]*\'?),?\s?(\'?[a-z]+-?[a-z]*\'?)?,?\s?(\'?[a-z]+-?[a-z]*\'?)?')

    pattern_verb_function = re.compile(r'([a-zA-Z]+)\s?\(([a-zA-Z]+)\)\s?:\s?([A-Za-z]+)'
                                       r'//verb,\s?(\'?[a-z]+-?[a-z]*\'?),?\s?(\'?[a-z]+-?[a-z]*\'?)?,?\s?(\'?[a-z]+-?[a-z]*\'?)?')
    matches_rel = pattern_verb_relation.finditer(idp_voc)
    for i in matches_rel:
        add_to_dictionary_function_false(i)
        generate_verb_entries(i)

    matches_funct = pattern_verb_function.finditer(idp_voc)
    for i in matches_funct:
        add_to_dictionary_function_true(i)
        generate_verb_entries(i)

#adds adjectives to the lexicon
def generate_adjectives_entries(annotations):
    if annotations[3]:
        a = annotations[4].split('-')
        if annotations[6]:
            lexicon.append(
                "adj_tr('{0}','{0}',{3}).\nadj_tr_comp('{1}','{0}',{3}).\nadj_tr_sup('{2}','{0}',{3}).\n".format(
                    annotations[4],
                    annotations[5],
                    annotations[6],
                    a[1]))
        else:
            lexicon.append("adj_tr('{0}','{0}',{1}).\n".format(annotations[4], a[1]))
    else:
        if annotations[6]:
            lexicon.append(
                "adj_itr({0},{0}).\nadj_itr_comp({1},{0}).\nadj_itr_sup({2},{0}).\n".format(annotations[4],
                                                                                            annotations[5],
                                                                                            annotations[6]))
        else:
            lexicon.append("adj_itr({0},{0}).\n".format(annotations[4]))

#detects adjective entries
def generate_adjectives(idp_voc):
    pattern_adjectives_relation = re.compile(
        r'([a-zA-Z]+)\s?\(+([a-zA-Z]+),?\s?([a-zA-Z]*)\)\s?//\s?adj,\s?(\'?[a-z]+-?[a-z]*\'?),?\s?(\'?[a-z]+-?['
        r'a-z]*\'?)?,?\s?(\'?[a-z]+-?[a-z]*\'?)?')
    pattern_adjectives_function = re.compile(r'([a-zA-Z]+)\(([a-zA-Z]+)\):([A-Za-z]+)'
                             r'//adj,\s?(\'?[a-z]+-?[a-z]*\'?),?\s?(\'?[a-z]+-?[a-z]*\'?)?,?\s?(\'?[a-z]+-?[a-z]*\'?)?')
    matches_adjectives = pattern_adjectives_relation.finditer(idp_voc)
    for i in matches_adjectives:
        add_to_dictionary_function_false(i)
        generate_adjectives_entries(i)

    matches_functions = pattern_adjectives_function.finditer(idp_voc)
    for i in matches_functions:
        add_to_dictionary_function_true(i)
        generate_adjectives_entries(i)

#clears lexicon, function dummies and links
# calls the other methods to generate the output
def generate_lexicon(idp_voc):
    lexicon.clear()
    link_IDP_Attempto.clear()
    functions_IDP.clear()
    generate_types(idp_voc)
    generate_constructor_types(idp_voc)
    generate_verbs(idp_voc)
    generate_adjectives(idp_voc)
    lexicon_output = ''.join(lexicon)
    return [lexicon_output, link_IDP_Attempto, functions_IDP]
