from surlex.grammar import Parser, RegexScribe, get_all_nodes, MacroTagNode
from surlex.macros import MacroRegistry, DefaultMacroRegistry
from surlex import grammar
import re

class Surlex(object):
    def __init__(self, surlex, macro_registry=DefaultMacroRegistry()):
        self.translated = False
        self.surlex = surlex
        self.macro_registry = macro_registry

    def translate(self):
        self.parser = Parser(self.surlex)
        self.node_list = self.parser.get_node_list()
        self.scribe = RegexScribe(
            self.node_list,
            self.macro_registry,
        )
        self.regex = self.scribe.translate()
        return self.regex

    @property
    def groupmacros(self):
        macros = {}
        if not self.translated:
            self.translate()
        for node in get_all_nodes(self.node_list):
            if isinstance(node, MacroTagNode):
                macros[node.name] = node.macro
        return macros

    @property
    def to_regex(self):
        if not self.translated:
            self.translate()
        return self.regex

    def match(self, subject):
        m = re.match(self.to_regex, subject)
        if m:
            return m.groupdict()

    def reverse_match(self, args):
        return reverse_match(self,args)

# This allows "surlex.register_macro" to register to the default registry
register_macro = DefaultMacroRegistry.register

def surlex_to_regex(surlex):
    parser = Parser(surlex)
    scribe = RegexScribe(parser.get_node_list())
    return scribe.translate()

def parsed_surlex_object(surlex):
    object = Surlex(surlex)
    object.translate()
    return object

def match(surlex, subject):
    return Surlex(surlex).match(subject)

def reverse_match(surlex, args):
    dict_mode = False
    if isinstance(args,dict):
        dict_mode = True
    else:
        #FIXME check if we have list here
        args = args[:]
    if not isinstance(surlex,Surlex):
        surlex = Surlex(surlex)
    surlex.translate()  # <for node list
    result = ""
    for node in surlex.node_list:
        if isinstance(node,grammar.TextNode):
            result = result + node.token
        if isinstance(node,grammar.TagNode):
            if dict_mode:
                if args.get(node.name):
                    result = result + str(args.get(node.name))
                else:
                    return
            elif len(args):
                result = result + str(args.pop(0))
            else:
                return 
    #FIXME : check extra args
    return result
