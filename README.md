# IDP-Attempto-Converter
## Requirements
* The ACE Editor can be installed from https://github.com/AceWiki/AceWiki.
* A web-IDE of the IDP system is available at http://verne.cs.kuleuven.be/idp/, for offline use, IDP can be installed from https://dtai.cs.kuleuven.be/software/idp.
## Introduction
- The aim is to facilitate the use of IDP for domain-experts who are not experienced with FO(.). To achieve this, we allow domain-experts to express their knowledge about a problem in Attempto Controlled English (ACE).  
- The user annotates an IDP vocabulary, according to the annotation rules, our program converts this to an ACE lexicon.
- With this lexicon, the user can express knowledge in ACE sentences with the assistance of the predictive ACE editor.
- These sentences are then parsed to discourse representation structures (DRS) by the Attempto Parsing Engine (APE), integrated in the ACE editor.
- These DRS can be converted to IDP theory by our program.

## Annotation rules
Annotations always start with //
* `types` are annotateded with a noun, the structure is  `//singular_form_noun, plural_form_noun`
* `constructed types`are annotated with a noun, followed by the genders in braces (masc, fem,neut): `//singular_form_noun,plural_form_noun,{gender_constructor_1,gender_constructor2,...}`
* `functions` and `relations` can be annotated with adjecives or verbs according to the user's preference.
  * Verb annotation 
      * unary `//verb,inf_form_verb,third_person_singular_verb` note that `verb` is a keyword, e.g. `//verb,change,changes`
     * binary `//verb,inf_form_verb,third_person_singular_verb,past_part_verb` note that `verb` is a keyword, e.g. `//verb,give,gives,given`
  * Adjective annotation
     * regular adjectives `//adj,positive_form`, e.g. `//adj,important`
     * irregular adjectives `//adj,positive_form,comparative_form,superlative_form`, e.g `//adj,happy,happier,happiest`
     
## Commands
### Generating an ACE Lexicon from an annotated IDP vocabulary
In the python command-line, to generate an ACE lexicon the user can type:
```
lexicon, mapping, function_dummy = main_converter.get_lexicon_and_mapping(annotated_IDP_vocabulary)
```
- lexicon :  The generated lexicon that can be used in the ACE Editor.
- mapping :  The correspondance between the IDP names and the lexicon words. 
- function_dummy:  Wheter the words in the lexicon correspond to a function in the IDP vocabulary. 

### Converting DRS to IDP theory
To convert DRS to IDP theory the user can type:
```
translation = main_converter.translate(drs_output_ace_editor, mapping, function_dummy)
```
- translation : The translation to IDP theory.

 
## Example
   We illustrate the annotations and commands with the map colouring problem:
```
import main_converter
annotated_voc_mc = """
type Area//area,areas
type Colour//colour,colours
Border(Area,Area)//verb,border,borders,bordered
Coloured(Area):Color//adj,coloured-with"""
lexicon, mapping, function_dummy = main_converter.get_lexicon_and_mapping(annotated_voc_mc)
print(lexicon)
print(mapping)
```
returns
```
noun_sg(area,area,neutr).
noun_pl(areas,area,neutr).
noun_sg(colour,colour,neutr).
noun_pl(colours,colour,neutr).
tv_finsg(borders,border).
tv_infpl(border,border).
tv_pp(bordered,border).
adj_tr('coloured-with','coloured-with',with).
[('area', 'Area'), ('colour', 'Colour'), ('border', 'Border'), ("'coloured-with'", 'Coloured')]
```
We express in the ACE editor that adjacent countries can not have the same colour: 
`if an area X is coloured-with a colour Z and borders an area Y then Y is not coloured-with Z.`
Note that the border relation has to be defined for both areas (Border(Belgium,Germany) and Border(Germany,Belgium))

The ACE editor parses this to DRS that we set equal to drs_output:
```
drs_output = "drs([],[=>(drs([A,B,C,D,E,F],[object(A,area,countable,na,eq,1),object(B,colour,countable,na,eq,1),property(C,'coloured-with',pos,B),predicate(D,be,A,C),object(E,area,countable,na,eq,1),predicate(F,border,A,E)]),drs([],[-(drs([G,H],[property(G,'coloured-with',pos,B),predicate(H,be,E,G)]))]))])"
translation = main_converter.translate(drs_output, mapping, function_dummy)
print(translation)
```
returns
```
((! a[Area] :! b[Colour] :! c[Area] :((Coloured(a)=b) & Border(a, c))=>(~((Coloured(c)=b))))).
```

