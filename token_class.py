import re

# the token class assumes as its argument a dictionary with with the following keys:
# id, form, lemma, upos, xpos, feats, head, deprel, deps, misc.

simple_equivalents = ['ccomp', 'nsubj', 'nsubj:pass', 'csubj', 'csubj:pass', 'nummod', 'nmod:poss', 'xcomp', 'obl', 'amod', 'nmod', 'iobj', 'det:poss', 'obj', 'obl:arg', 'advmod', 'case', 'root', 'expl:pv']

def is_simp_equiv(deprel):
    if deprel in simple_equivalents:
        return True

    return False

complex_equivalents = {
    'auxilliaries': ['aux:pass', 'aux'],
    'determiners': ['det'],
    'compounds': ['flat', 'flat:name', 'compound', 'compound:prt'],
    'clausal_modifiers': ['appos', 'advcl', 'acl'],
    'complex_preds': ['expl', 'cop']
}

def is_comp_equiv(deprel):
    for key in complex_equivalents:
        if deprel in complex_equivalents[key]:
            return True

    return False

no_equivalents = {
    'sentence': ['reparandum', 'orphan', 'vocative'],
    'token': ['punct', 'discourse', 'mark']
}

def is_not_equiv(deprel):
    for key in no_equivalents:
        if deprel in no_equivalents[key]:
            return True
    
    return False

coordinants = ['conj', 'cc', 'parataxis']

def is_coordinant(deprel):
    if deprel in coordinants:
        return True

    return False

def is_deprel(deprel):
    if is_simp_equiv(deprel) == True or is_comp_equiv(deprel) == True or is_not_equiv(deprel) == True or is_coordinant(deprel) == True:
        return True
    
    return True

# every subset of deprels and their subsets are assigned and functions are defined to return True or False values for if a deprel is in a given subset.

generate_feat_gfs = input('automatically generate nonargument GFs from UD annotation?\ny/n: ')

class Token:
    def __init__(self, token):
        self.id = None
        self.id = token['id']

        self.form = None
        self.form = token['form']

        self.lemma = None
        self.lemma = token['lemma']

        self.upos = None
        self.upos = token['upos']

        self.feats = None

        if token['feats'] != '_':
            self.feats = token['feats']

        self.head = None
        self.head = token['head']

        self.deprel = None
        self.deprel = token['deprel']

        # most information in the UD annotation is stored in token objects and will be referred to in complex conversions and elsewhere.

        self.subtype = None

        if is_simp_equiv(self.deprel) == True:
            self.subtype = 'simple'

        elif is_comp_equiv(self.deprel) == True:
            if self.deprel in complex_equivalents['auxilliaries']:
                self.subtype = 'auxilliary'

            elif self.deprel in complex_equivalents['determiners']:
                self.subtype = 'determiner'

            elif self.deprel in complex_equivalents['compounds']:
                self.subtype = 'compound'

            elif self.deprel in complex_equivalents['clausal_modifiers']:
                self.subtype = 'clausal_modifier'

            elif self.deprel in complex_equivalents['complex_preds']:
                self.subtype = 'complex_pred'

        elif is_coordinant(self.deprel) == True:
            self.subtype = 'coordinant'

        # the token is given a subtype which will be used to call an appropriate conversion method.

        self.gf = None
        self.value = None
        self.arg = None

        # the grammatical function, value and argument properties are generated by the conversion methods below.

        self.dependants = []
        self.arguments = []

        # the dependants and arguments lists are appended during the conversion (see. nest_order() and f_compose(sentence)) and required by pred_format().

    def convert_simple(self):
        if self.deprel == 'root':
            self.arg = True

            return 'ROOT', {'PRED': '{}< >'.format(self.lemma)}

        elif self.deprel == 'nsubj':
            self.arg = True

            return 'SUBJ', {'PRED': '{}< >'.format(self.lemma)}

        elif self.deprel == 'nsubj:pass':
            self.arg = True

            return 'SUBJ', {'PRED': '{}< >'.format(self.lemma)}

        elif self.deprel == 'csubj':
            self.arg = True

            return 'SUBJ', {'PRED': '{}< >'.format(self.lemma)}

        elif self.deprel == 'csubj:pass':
            self.arg = True

            return 'SUBJ', {'PRED': '{}< >'.format(self.lemma)}

        elif self.deprel == 'obj':
            self.arg = True

            return 'OBJ', {'PRED': '{}< >'.format(self.lemma)}

        elif self.deprel == 'expl:pv':
            self.arg = True

            return 'OBJ', {'PRED': '{}< >'.format(self.lemma)}

        elif self.deprel == 'iobj':
            self.arg = True

            return 'OBJ:IND', {'PRED': '{}< >'.format(self.lemma)}

        elif self.deprel == 'obl':
            self.arg = True

            return 'OBL', {'PRED': '{}< >'.format(self.lemma)}

        elif self.deprel == 'obl:arg':
            self.arg = True

            return 'OBL', {'PRED': '{}< >'.format(self.lemma)}

        elif self.deprel == 'ccomp':
            self.arg = True

            return 'COMP', {'PRED': '{}< >'.format(self.lemma)}

        elif self.deprel == 'xcomp':
            self.arg = True

            return 'XCOMP', {'PRED': '{}< >'.format(self.lemma),
                            'SSUBJ': '(SUBJ^)'}

        elif self.deprel == 'nmod':
            self.arg = False

            return 'ADJ', [{'PRED': '{}< >'.format(self.lemma)}]

        elif self.deprel == 'nmod:poss':
            self.arg = False

            return 'POSS', {'PRED': '{}< >'.format(self.lemma)}

        elif self.deprel == 'nummod':
            self.arg = False

            return 'SPEC', {'PRED': '{}< >'.format(self.lemma)}

        elif self.deprel == 'amod':
            self.arg = False

            return 'ADJ', [{'PRED': '{}< >'.format(self.lemma)}]
        
        elif self.deprel == 'advmod':
            self.arg = False

            return 'ADJ', [{'PRED': '{}< >'.format(self.lemma)}]

        elif self.deprel == 'det:poss':
            self.arg = False

            return 'POSS', {'PRED': '{}< >'.format(self.lemma)}
        
        elif self.deprel == 'case':
            self.arg = False

            try:
                if 'Case' in self.feats.keys():
                    return 'CASE', {'PRED': self.feats['Case'].upper()}

                else:
                    return 'CASE', {'PRED': self.lemma.upper()}

            except:
                return 'CASE', {'PRED': self.lemma.upper()}

        else:
            return 'NONE', {'NONE': 'NONE< >'}

    def convert_auxilliaries(self):
        self.arg = False

        return '*CPOUND', {'PRED': '{}-'.format(self.form)}

    def convert_determiners(self):
        definite_articles = ['der', 'die', 'das', 'des', 'den', 'dem']
        indefinite_articles = ['ein', 'eine', 'eines', 'einen', 'einem']

        self.arg = False

        if self.upos == 'DET':
            if self.lemma.lower() in definite_articles:
                return 'DEF', {'BOOL': '+'}

            elif self.lemma.lower() in indefinite_articles:
                return 'DEF', {'BOOL': '-'}

            else:
                return 'SPEC', {'PRED': '{}< >'.format(self.lemma)}
            
        elif self.upos == 'PRON':
            return 'POSS', {'PRED': '{}< >'.format(self.lemma)}

    def convert_compounds(self):
        self.arg = False

        if self.deprel == 'compound:prt':
            return '*CPOUND', {'PRED': '{}'.format(self.lemma)}

        else:
            return '*CPOUND', {'PRED': '-{}'.format(self.lemma)}

        # the dummy gf '*CPOUND' will not be part of the f_structure, it's just a marker.

    def convert_claus_mods(self):
        self.arg = False

        return 'ADJ', [{'PRED': '{}< >'.format(self.lemma)}]

        # see. report section 3.1.2.5 for a record of the problems here.

    def convert_comp_preds(self):
        if self.deprel == 'expl':
            self.arg = True

            return '*SUBJ', {'PRED': '{}< >'.format(self.lemma)}

        elif self.deprel == 'cop':
            self.arg = False

            return 'COP', {'PRED': '{}< >'.format(self.form)}

    def convert_coordinants(self):
        if self.deprel == 'conj':
            self.arg = False

            return '*COORD', [{'PRED': '{}< >'.format(self.lemma), 'COORD': 'LIST'}]

            # conjunts have the coordination type LIST, because if this type is not updated by a dependant with the relation 'cc' (below), it probably is.
            # the dummy gf '*COORD' will not be part of the f_structure, it's just a marker.

        elif self.deprel == 'parataxis':
            self.arg = False

            return '*COORD', [{'PRED': '{}< >'.format(self.lemma), 'COORD': 'PARATAXIS'}]

        elif self.deprel == 'cc':
            self.arg = False

            return 'COORD', {'PRED': '{}'.format(self.lemma).upper()}

            # the only purpose of the value of coordinating words like is to update the coordination type of the conjunct.

    def generate_feat_gfs(self):
        feat_gf_upos = ['NOUN', 'VERB', 'PRON', 'PROPN']

        if type(self.feats) == dict:
            if self.upos in feat_gf_upos:
                if 'Case' in self.feats.keys():
                    try:
                        self.value['CASE'] = self.feats['Case'].upper()

                    except:
                        self.value[0]['CASE'] = self.feats['Case'].upper()
            
                if 'Gender' in self.feats.keys():
                    try:
                        self.value['GEN'] = self.feats['Gender'].upper()

                    except:
                        self.value[0]['GEN'] = self.feats['Gender'].upper()
            
                if 'Number' in self.feats.keys():
                    try:
                        self.value['NUM'] = self.feats['Number'].upper()

                    except:
                        self.value[0]['NUM'] = self.feats['Number'].upper()
            
                if 'Person' in self.feats.keys():
                    try:
                        self.value['PERS'] = self.feats['Person'].upper()

                    except:
                        self.value[0]['PERS'] = self.feats['Person'].upper()
            
                if 'Mood' in self.feats.keys():
                    try:
                        self.value['MOOD'] = self.feats['Mood'].upper()

                    except:
                        self.value[0]['MOOD'] = self.feats['Mood'].upper()

                if 'Person' in self.feats.keys():
                    try:
                        self.value['PERS'] = self.feats['Person'].upper()

                    except:
                        self.value[0]['PERS'] = self.feats['Person'].upper()

                if 'Tense' in self.feats.keys():
                    try:
                        self.value['TENSE'] = self.feats['Tense'].upper()

                    except:
                        self.value[0]['TENSE'] = self.feats['Tense'].upper()

                if 'Aspect' in self.feats.keys():
                    try:
                        self.value['ASP'] = self.feats['Aspect'].upper()

                    except:
                        self.value[0]['ASP'] = self.feats['Aspect'].upper()

    def convert(self):
        if self.subtype == 'simple':
            self.gf, self.value = self.convert_simple()

        elif self.subtype == 'auxilliary':
            self.gf, self.value = self.convert_auxilliaries()

        elif self.subtype == 'determiner':
            self.gf, self.value = self.convert_determiners()

        elif self.subtype == 'compound':
            self.gf, self.value = self.convert_compounds()

        elif self.subtype == 'clausal_modifier':
            self.gf, self.value = self.convert_claus_mods()

        elif self.subtype == 'complex_pred':
            self.gf, self.value = self.convert_comp_preds()
        
        elif self.subtype == 'coordinant':
            self.gf, self.value = self.convert_coordinants()

        else:
            self.gf, self.value = self.convert_simple()

        if generate_feat_gfs.lower() == 'y':
            self.generate_feat_gfs()

        # self.convert() returns two values: a key and a value for the f_structure dictionary of this token.

# in sum, the Token class stores data from the filtered sentences and has methods for conversion to grammatical functions.