from pyparsing import (Suppress, Word, Group, delimitedList, sglQuotedString, alphas, nums, Literal, Forward, Optional,
                       ParseResults)
import re
import lexicon_generator

variables = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j',
             'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z']
link_IDP_Attempto = {}
functions_IDP = {}


class Property:
    def __init__(self, ref, predicate, fixed):
        self.ref = ref
        self.predicate = predicate
        self.fixed = fixed

    def to_string(self, arg):
        return "{0}({1})".format(lexicon_to_voc(self.predicate), arg)


class PropertyTrans(Property):
    def __init__(self, ref, predicate, fixed, open):
        super().__init__(ref, predicate, fixed)
        self.open = open

    def to_string(self, arg):
        if functions_IDP[self.predicate]:
            return "({0}({1})={2})".format(lexicon_to_voc(self.predicate), arg, self.open.to_string())
        else:
            return "{0}({1}, {2})".format(lexicon_to_voc(self.predicate), arg, self.open.to_string())


class Object:
    # Other fields are not necessary but left in for possible extensions
    def __init__(self, ref, noun, objclass, unit, op, count):
        self.ref = ref
        self.noun = noun
        self.objclass = objclass
        self.unit = unit
        self.op = op
        self.count = count
        self.var = variables[0]
        del variables[0]

    def to_string(self):
        return self.var

    def to_string2(self):
        if self.noun == 'something':
            return "{0}".format(self.var)
        else:
            return "{0}[{1}] ".format(self.var, lexicon_to_voc(self.noun))

    def to_string3(self, arg):
        return "{0}({1})".format(lexicon_to_voc(self.noun), arg)


class NamedObject:
    def __init__(self, string):
        self.string = string
        self.ref = ''

    def to_string(self):
        return self.string


class PropertyPredicate:
    def __init__(self, ref, noun, obj, subj):
        self.ref = ref
        self.noun = noun
        self.obj = obj
        self.subj = subj

    def to_string(self):
        if isinstance(self.subj, Object):
            return self.subj.to_string3(self.obj.to_string())
        else:
            return self.subj.to_string(self.obj.to_string())


class Predicate:
    # upgrade for unary predicates necessary
    def __init__(self, ref, predicate, subjref):
        self.ref = ref
        self.predicate = predicate
        self.subjref = subjref

    def to_string(self):
        return "{0}({1})".format(lexicon_to_voc(self.predicate), self.subjref.to_string())


class PredicateTrans(Predicate):
    def __init__(self, ref, predicate, subjref, objref):
        super().__init__(ref, predicate, subjref)
        self.objref = objref

    def to_string(self):
        if functions_IDP[self.predicate]:
            return "{0}({1})= {2}".format(lexicon_to_voc(self.predicate), self.subjref.to_string(),
                                          self.objref.to_string())
        else:
            return "{0}({1}, {2})".format(lexicon_to_voc(self.predicate), self.subjref.to_string(),
                                          self.objref.to_string())


def lexicon_to_voc(s):
    # link words
    return link_IDP_Attempto[s]


# punctuation and basic elements
LPAR, RPAR, LSQB, RSQB, COMMA = map(Suppress, "()[],")

referent_expr = Word(alphas)
lexicon_entry_expr = Word(alphas) | sglQuotedString

named_key = Literal("named")
named_expr = Group(named_key + LPAR + sglQuotedString + RPAR)
general_ref_expr = named_expr | referent_expr

object_key = "object"
noun_expr = lexicon_entry_expr
object_class_expr = Literal("dom") | Literal("mass") | Literal("countable")
unit_expr = lexicon_entry_expr
operator_expr = Literal("eq") | Literal("geq") | Literal("greater") | Literal("leq") | Literal("less") | Literal(
    "exactly") | Literal("na")
count_expr = Literal("na") | Word(nums)
object_expr = Group(
    object_key + LPAR + referent_expr + COMMA + noun_expr + COMMA + object_class_expr + COMMA + unit_expr + COMMA + operator_expr + COMMA + count_expr + RPAR)

property_key = "property"
adjective_expr = lexicon_entry_expr
degree_expr = Literal("pos") | Literal("posas") | Literal("comp") | Literal("compthan") | Literal("sup")

property_predicate_1_ary_expr = Group(
    property_key + LPAR + referent_expr + COMMA + adjective_expr + COMMA + degree_expr + RPAR)

property_predicate_2_ary_expr = Group(
    property_key + LPAR + referent_expr + COMMA + adjective_expr + COMMA + degree_expr + COMMA + general_ref_expr + RPAR)

comp_target_expr = Literal("subj") | Literal("obj")

property_predicate_3_ary_expr = Group(
    property_key + LPAR + referent_expr + COMMA + adjective_expr + COMMA + general_ref_expr + COMMA + degree_expr + COMMA + comp_target_expr + COMMA + general_ref_expr + RPAR)

property_predicate_expr = property_predicate_1_ary_expr | property_predicate_2_ary_expr | property_predicate_3_ary_expr

predicate_key = "predicate"
verb_expr = lexicon_entry_expr
subject_ref_expr = general_ref_expr
object_ref_expr = general_ref_expr
indirect_object_ref_expr = general_ref_expr

predicate_predicate_itr_expr = Group(
    predicate_key + LPAR + referent_expr + COMMA + verb_expr + COMMA + subject_ref_expr + RPAR)
predicate_predicate_tr_expr = Group(
    predicate_key + LPAR + referent_expr + COMMA + verb_expr + COMMA + subject_ref_expr + COMMA + object_ref_expr + RPAR)
predicate_predicate_dtr_expr = Group(
    predicate_key + LPAR + referent_expr + COMMA + verb_expr + COMMA + subject_ref_expr + COMMA + object_ref_expr + COMMA + indirect_object_ref_expr + RPAR)
predicate_predicate_expr = predicate_predicate_itr_expr | predicate_predicate_tr_expr | predicate_predicate_dtr_expr

domain_expr = Group(LSQB + Optional(delimitedList(referent_expr)) + RSQB)
condition_expr = Forward()
conditions_expr = Group(LSQB + Optional(delimitedList(condition_expr)) + RSQB)

drs_key = "drs"
drs_expr = Group(drs_key + LPAR + domain_expr + COMMA + conditions_expr + RPAR)

negation_key = Literal("-")
negation_drs_expr = Group(negation_key + LPAR + drs_expr + RPAR)
implication_key = Literal("=>")
if_then_drs_expr = Group(implication_key + LPAR + drs_expr + COMMA + drs_expr + RPAR)
disjunction_key = Literal("v")
disjunction_drs_expr = Group(disjunction_key + LPAR + Optional(delimitedList(drs_expr)) + RPAR)

condition_expr << (
        object_expr | property_predicate_expr | predicate_predicate_expr | negation_drs_expr | if_then_drs_expr | disjunction_drs_expr)


def sampelize(string):
    pattern = re.compile(r'\-\d\/\d+')
    return re.sub(pattern, '', string)


dict = {}
universal = {}
voc = []


def doorzoek_lijst(l, in_if=False):
    if type(l) is list:
        if l[0] == 'drs':
            # l[1] is lijst van referenten
            # l[2] zijn de condities
            for x in l[2]:
                if len(x) > 3 and type(x[3]) is list:
                    if x[3][0] == 'named':
                        x[3] = x[3][1]
                        dict[x[3]] = NamedObject(x[3][1:-1])
                if len(x) > 4 and type(x[4]) is list:
                    if x[4][0] == 'named':
                        x[4] = x[4][1]
                        dict[x[4]] = NamedObject(x[4])

                if x[0] == 'object':
                    dict[x[1]] = Object(x[1], x[2], x[3], x[4], x[5], x[6])
                    # dictionary[x[1]] = ...
                    if in_if:
                        universal[x[1]] = True
                    else:
                        universal[x[1]] = False
                    # voeg toe aan dictionary
                elif x[0] == 'predicate':
                    if len(x) > 4:
                        if x[2] == 'be':
                            dict[x[1]] = PropertyPredicate(x[1], x[2], dict[x[3]], dict[x[4]])
                        else:
                            dict[x[1]] = PredicateTrans(x[1], x[2], dict[x[3]], dict[x[4]])
                    else:
                        dict[x[1]] = Predicate(x[1], x[2], dict[x[3]])
                elif x[0] == 'property':
                    if len(x) > 4:
                        dict[x[1]] = PropertyTrans(x[1], x[2], x[3], dict[x[4]])
                    else:
                        dict[x[1]] = Property(x[1], x[2], [x[3]])
                elif x[0] == '-':
                    doorzoek_lijst(x[1])
                elif x[0] == '=>':
                    doorzoek_lijst(x[1], True)
                    doorzoek_lijst(x[2])
                elif x[0] == 'v':
                    for i in range(1, len(x)):
                        doorzoek_lijst(x[i])


def to_string(l):
    str_translation = []
    if type(l) is list:
        if l[0] == 'drs':
            objects = []
            for x in l[2]:
                if x[0] == 'object':
                    objects.append(x)
            str_list = []
            for obj in objects:
                if universal[obj[1]]:
                    str_list.append('! {0}:'.format(dict[obj[1]].to_string2()))
                else:
                    str_list.append(' ? {0}:'.format(dict[obj[1]].to_string2()))
            str_translation.append(''.join(str_list))
            str_translation.append('(')
            condities = [c for c in l[2] if c[0] != 'property' and c[0] != 'object']
            for j in range(0, len(condities)):
                str_translation.append(to_string(condities[j]))
                if j < len(condities) - 1:
                    str_translation.append(' & ')
            str_translation.append(')')
        elif l[0] == '=>':
            str_translation.append('(')
            str_translation.append(to_string(l[1]))
            str_translation.append('=>')
            str_translation.append(to_string(l[2]))
            str_translation.append(')')
        elif l[0] == '-':
            str_translation.append('~')
            str_translation.append(to_string(l[1]))
        elif l[0] == 'v':
            str_translation.append('(')  # conditioneel als len(l) > 2
            length = len(l)
            for i in range(1, length):
                str_translation.append(to_string(l[i]))
                if i != length - 1:
                    str_translation.append(' | ')
        elif l[0] == 'predicate':
            str_translation.append(dict[l[1]].to_string())
        return ''.join(str_translation)


def variable_reset():
    variables.clear()
    variables.extend(['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j',
                     'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z'])


def string_cleanup(s):
    pattern = re.compile(r'\(\)\=\>')
    return re.sub(pattern, '', s)


def add_to_dict(list):
    link_IDP_Attempto.clear()
    functions_IDP.clear()
    for i in list[0]:
        link_IDP_Attempto[i[0]] = i[1]
    for j in list[1]:
        functions_IDP[j[0]] = j[1]


def get_lexicon_and_mapping(input_lexicon):
    output_generator = lexicon_generator.generate_lexicon(input_lexicon)
    return output_generator[0], output_generator[1], output_generator[2]


def translate(drs_input, mapping, function_dummy):
    add_to_dict([mapping, function_dummy])
    parsed = drs_expr.parseString(sampelize(drs_input)).asList()
    doorzoek_lijst(parsed[0])
    result_clean = string_cleanup(to_string(parsed[0])) + "."
    variable_reset()
    return result_clean
