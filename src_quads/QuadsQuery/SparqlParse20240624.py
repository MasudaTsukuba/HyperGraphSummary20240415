"""
SparqlParse20240624.py
2024/6/24, T. Masuda
Amagasa Laboratory, University of Tsukuba
"""
import os
import re
import json

from pyparsing import (
    Word, alphas, alphanums, nums, quoted_string, sgl_quoted_string, dbl_quoted_string, Literal, Group, OneOrMore, Optional, ZeroOrMore,
    Keyword, Combine, Suppress, delimitedList, Forward, quotedString, sglQuotedString, dblQuotedString, infixNotation, opAssoc, oneOf
)  # use pyparsing


class SparqlParse:
    graph_index = 1

    def __init__(self):
        self.blank_node_id = 1
        # Define basic components
        # IRIREF = quotedString
        IRIREF = Suppress('<') + Word(alphas, alphanums + '_' + '-' + '/' + ':' + '#' + '.') + Suppress('>')

        VAR1 = Combine(Literal('?') + Word(alphanums + '_'))
        VAR2 = Combine(Literal('$') + Word(alphanums + '_'))
        var = VAR1 | VAR2  # variable

        # Define prefixes and base declarations
        BASE = Keyword("BASE")
        PREFIX = Keyword("PREFIX")
        # IRIREF = quotedString
        # prefix name space
        PNAME_NS = Word(alphas, alphanums + '_' + '#') + Literal(':') | Literal('') + Literal(':')  # ends with :
        # prefix declaration
        prefixDecl = Group(PREFIX + PNAME_NS + IRIREF)
        # base declaration
        baseDecl = Group(BASE + IRIREF)

        # Define keywords
        SELECT = Keyword("SELECT")
        DISTINCT = Keyword("DISTINCT")
        WHERE = Keyword("WHERE")
        FROM = Keyword("FROM")
        UNION = Keyword("UNION")  # 2024/6/24
        OPTIONAL = Keyword("OPTIONAL")  # 2024/7/1
        NAMED = Keyword("NAMED")
        LIMIT = Keyword("LIMIT")  # | Keyword("Limit")  # 2024/7/1
        OFFSET = Keyword("OFFSET")
        FILTER = Keyword("FILTER")
        STR = Keyword("STR")
        ORDER = Keyword("ORDER")
        BY = Keyword("BY")

        # Define basic RDF elements
        # rdfLiteral = quotedString | sglQuotedString | dblQuotedString | quoted_string | sgl_quoted_string | dbl_quoted_string
        rdfLiteral = quotedString
        # rdfLiteral = Word(alphanums + ' ' + '_' + '-' + '/' + ':' + '#' + '.' + '"' + "'")
        integer = Word(nums)
        numericLiteral = integer
        booleanLiteral = Keyword("true") | Keyword("false")
        literal = rdfLiteral | numericLiteral | booleanLiteral

        # iri = IRIREF | Combine(PNAME_NS + Word(alphanums + '_'))
        iri = IRIREF | Group(PNAME_NS + Word(alphanums + '_')) | Group(PNAME_NS)
        blankNode = Combine('_:' + Word(alphanums + '_')) | Group(Suppress('[') + Suppress(']'))
        # collection = Forward()
        # object_ = var | iri | literal | blankNode | collection
        object_ = var | iri | literal | blankNode

        subject = var | iri | blankNode   # | collection
        verb = var | iri | Keyword("a")  # predicate
        # objectList = Group(delimitedList(object_))
        objectList = object_  # 2024/7/3
        predicateObjectList = Group(Group(verb + objectList) + ZeroOrMore(Suppress(";") + Group(verb + objectList)))

        # triples and triples block
        triplesBlock = Group(subject + predicateObjectList) | Group(Suppress('[') + predicateObjectList + Suppress(']'))
        triplesBlockList = Group(triplesBlock + ZeroOrMore(Suppress(".") + ZeroOrMore(triplesBlock)))

        # groupGraphPattern = Suppress("{") + Optional(triplesBlockList) + Suppress("}")
        # datatype = Combine(Literal('^^xsd:') + Word(alphas))
        datatype = Suppress('^^') + Group(PNAME_NS + Word(alphanums + '_'))
        factor = (var | iri
                  | Group('LANG' + Suppress('(') + var + Suppress(')'))
                  | Group(STR + Suppress('(') + var + Suppress(')'))
                  | Group(literal + Optional(datatype)))
        expression = infixNotation(factor,
                                   [
                                       (oneOf("!"), 1, opAssoc.RIGHT),
                                       (oneOf("+ -"), 1, opAssoc.RIGHT),  # 符号は最優先。
                                       (oneOf("* /"), 2, opAssoc.LEFT),  # 掛け算割り算は足し算引き算より優先
                                       (oneOf("+ -"), 2, opAssoc.LEFT),
                                       (oneOf("= != > >= < <="), 2, opAssoc.LEFT),
                                       (oneOf("&& ||"), 2, opAssoc.LEFT),
                                   ]
                                   )
        filter = Group(FILTER + Suppress('(') + OneOrMore(expression) + Suppress(')'))

        triplesBlockListWithZeroOrMoreFilter = Group(triplesBlockList) + ZeroOrMore(filter)
        optionalExpression = Group(OPTIONAL + Suppress("{") + triplesBlockListWithZeroOrMoreFilter + Suppress("}"))
        basicGroupGraphPattern = Group(Group(triplesBlockListWithZeroOrMoreFilter
            + ZeroOrMore(optionalExpression)) + ZeroOrMore(filter))

        groupGraphPattern = Group(basicGroupGraphPattern) | Group(Suppress("{") + basicGroupGraphPattern + Suppress("}")) \
            + OneOrMore(Group(Suppress(UNION) + Suppress("{") + basicGroupGraphPattern) + Suppress("}"))

        whereClause = Suppress(Optional(WHERE)) + Suppress("{") + groupGraphPattern + Suppress("}")

        # Define the query structure
        limitExpression = Group(LIMIT + Word(nums))
        orderbyExpression = Group(ORDER + BY + Suppress("(") + VAR1 + Suppress(")"))
        selectQuery = SELECT + Group(Optional(DISTINCT)) + Group(OneOrMore(var) | "*") + whereClause + ZeroOrMore(limitExpression | orderbyExpression)

        # Define the full query structure with prologue
        self.query = Group(Optional(baseDecl)) + Group(ZeroOrMore(prefixDecl)) + selectQuery
        # self.query = Group(Optional(baseDecl)) + Group(OneOrMore(prefixDecl)) + selectQuery
        # self.query = Group(Optional(baseDecl)) + Group(ZeroOrMore(prefixDecl))  # 2024/5/21

    def convert_sparql(self, sparql_string):

        def convert_keyword_upper(sparql_string: str) -> str:
            def replace_to_upper(match):  # to upper case
                return match.group(0).upper()

            return_string = sparql_string
            keywords_to_replace = ["distinct", "limit", "prefix", "select", "where"]
            pattern = re.compile("|".join(keywords_to_replace), re.IGNORECASE)
            return_string = pattern.sub(replace_to_upper, sparql_string)
            return return_string

        def create_subject_json(term):
            pass

        def create_predicate_json(term):
            predicate_json = {}
            try:
                if type(term) == str:
                    if term.startswith('?'):  # predicate is a variable
                        predicate_json = {'termType': 'Variable', 'value': term.replace('?', '')}
                    elif term == 'a':  # type of
                        predicate_json = {'termType': 'NamedNode',
                                          'value': "http://www.w3.org/1999/02/22-rdf-syntax-ns#type"}
                    elif term.startswith('http'):  # named node
                        predicate_json = {'termType': 'NamedNode', 'value': term}
                    else:
                        pass  # unexpected
                elif len(term) == 3: # with a prefix
                    xxx = term[0]
                    yyy = term[2]
                    predicate_json = {'termType': 'NamedNode', 'value': working_prefixes[xxx] + yyy}
                elif len(term) == 1:  # prefix only
                    xxx = term[0]
                    predicate_json = {'termType': 'NamedNode', 'value': working_prefixes[xxx]}
                else:
                    pass  # unexpected
            except Exception as e:
                pass  # unexpected
            return predicate_json

        def create_object_json(term):
            object_json = {}
            try:
                if type(term) == str:
                    if term.startswith('?'):
                        object_json = {'termType': 'Variable', 'value': term.replace('?', '')}
                    elif term.startswith('http'):
                        object_json = {'termType': 'NamedNode', 'value': term}
                    else:
                        object_json = {'termType': 'Literal', 'value': term}
                elif len(term) == 3 and term[1] == ':':
                    xxx = term[0]
                    yyy = term[2]
                    object_json = {'termType': 'NamedNode', 'value': working_prefixes[xxx] + yyy}
                elif len(term) == 2 and term[0] == ':':
                    object_json = {'termType': 'NamedNode', 'value': working_prefixes[''] + term[1]}
                elif len(term) == 1:
                    xxx = term[0]
                    object_json = {'termType': 'NamedNode', 'value': working_prefixes[xxx]}
                else:
                    pass  # unexpected
            except Exception:
                pass  # unexpected
            return object_json

        def create_expression(term):
            def lang_operator(term):
                try:
                    args_lang = {'type': 'operation', 'operator': term[1]}
                    arg = {'type': 'operation', 'operator': 'lang',
                           'args': [{'termType': 'Variable', 'value': term[0][1].replace('?', '')}]}
                    args_lang['args'] = [arg]
                    arg = {'termType': 'Literal', 'value': term[2][0].replace("'", ''), 'language': '',
                           'datatype': {
                               'termType': 'NamedNode',
                               'value': 'http://www.w3.org/2001/XMLSchema#string'}}
                    args_lang['args'].append(arg)
                except Exception as e:
                    pass  # error
                return args_lang

            return_expression = {}
            expression = term
            args_filter = []
            left_term = expression[0]
            try:
                if left_term.startswith('?'):
                    left_term = left_term.replace('?', '')
                    return_expression = {'termType': 'Variable', 'value': left_term}
                    args_filter.append(return_expression)
                elif left_term == '!':
                    eee = create_expression([expression[1]])
                    return_expression = {"type": "operation", "operator": "!", "args": [eee]}
                    args_filter.append(return_expression)
                else:
                    raise Exception
            except Exception as e:
                try:
                    if left_term[0][0] == 'LANG':
                        args_lang = lang_operator(left_term)
                        args_filter.append(args_lang)
                        pass
                    else:
                        raise Exception
                except Exception as e:
                    try:
                        return_expression = create_expression(expression[0])
                        args_filter.append(return_expression)
                    except Exception as e:
                        pass  # error
                    pass
            left_json = {}
            try:
                operator = expression[1]
                right_term = expression[2]
                try:
                    yyy = list(right_term)
                    try:
                        datatype = working_prefixes[right_term[1][0]] + right_term[1][2]
                        args_filter.append({"termType": "Literal", "value": right_term[0].replace('"', ''), "language": "",
                                            "datatype": {'termType': 'NamedNode', 'value': datatype}})
                    except Exception:
                        try:
                            right_term2 = working_prefixes[right_term[0]] + right_term[2]
                            args_filter.append({'termType': 'NamedNode', 'value': right_term2})
                        except Exception:
                            try:
                                if len(list(right_term)) == 3:
                                    eee = create_expression(right_term)
                                    args_filter.append(eee)
                                elif right_term[0][0] == 'LANG':
                                    args_lang = lang_operator(right_term)
                                    args_filter.append(args_lang)
                                else:
                                    try:
                                        xxx = right_term[0]

                                        iii = int(xxx)
                                        args_filter.append(
                                            {"termType": "Literal", "value": str(iii),
                                             "language": "",
                                             "datatype": {'termType': 'NamedNode',
                                                          'value': 'http://www.w3.org/2001/XMLSchema#integer'}})
                                    except Exception as e:
                                        try:
                                            if type(right_term[0]) == str:
                                                aaa = str(right_term[0].replace("'", ""))
                                                args_filter.append(
                                                    {"termType": "Literal", "value": aaa,
                                                     "language": "",
                                                     "datatype": {'termType': 'NamedNode',
                                                                  'value': 'http://www.w3.org/2001/XMLSchema#string'}})
                                            else:
                                                operator = term[1]
                                                left_term = term[0]
                                                right_term = term[2]
                                                left_expression = create_expression(left_term)
                                                right_expression = create_expression(right_term)
                                                args_filter = [left_expression, right_expression]
                                        except Exception as e:
                                            pass  # error
                                        pass
                                    pass
                            except Exception:
                                pass
                    return_expression = {'type': 'operation', 'operator': operator, 'args': args_filter}
                    pass
                except IndexError:
                    pass
            except Exception as e:
                pass
            return return_expression

        def create_triple(triple):
            # create_triple = True
            try:
                subject = triple[0]
                if type(subject) == str:
                    if subject.startswith('?'):
                        subject_json = {'termType': 'Variable', 'value': subject.replace('?', '')}
                    else:  # named node without prefix
                        subject_json = {'termType': 'NamedNode', 'value': subject}
                elif len(list(subject)) == 3:  # named node with prefix
                    subject_json = {'termType': 'NamedNode',
                                    'value': working_prefixes[subject[0]] + subject[2]}
                elif len(list(subject)) == 0:  # blank node
                    subject_json = {'termType': 'BlankNode', 'value': 'blank' + str(self.blank_node_id)}
                    self.blank_node_id += 1
                else:
                    pass  # unexpected
                for predicate_object_pair in triple[1]:
                    predicate_json = create_predicate_json(predicate_object_pair[0])
                    object_json = create_object_json(predicate_object_pair[1])
                    arg = {'subject': subject_json, 'predicate': predicate_json, 'object': object_json}
            except Exception as e:
                pass
            return arg

        def create_where_clause_with_filter(where_term_with_filter):
            sparql_data_where_with_filter = []
            if len(where_term_with_filter) > 0:
                triples = []
                for triple in where_term_with_filter[0]:
                    triples.append(create_triple(triple))
                sparql_data_where_with_filter.append({'type': 'bgp', 'value': triples})
                if len(where_term_with_filter) == 2 and where_term_with_filter[1][0] == 'FILTER':
                    sparql_data_where_with_filter.append({'type': 'filter', 'value': create_expression(where_term_with_filter[1][1])})
                else:
                    pass  # unexpected
            return sparql_data_where_with_filter

        def create_where_clause_with_optional(where_term):
            sparql_data_where_with_optional = []
            # args = []
            # for component in where_term:
            component = where_term
            if len(component) > 0:
                xxx0 = component[0]
                sparql_data_where_with_optional.append({'type': 'mandatory', 'value': create_where_clause_with_filter(component[0])})
                if len(component) == 2:
                    xxx1 = component[1]
                    if component[1][0] == 'OPTIONAL':
                        sparql_data_where_with_optional.append({'type': 'optional', 'value': create_where_clause_with_filter(component[1][1])})
                else:
                    pass  # unexpected
            return sparql_data_where_with_optional

        # blank_node_id = 100
        sparql_data = {'type': 'query', 'queryType': 'SELECT'}
        working_prefixes = {}
        uppercase_sparql_string = convert_keyword_upper(sparql_string)
        parsed_sparql = self.query.parse_string(uppercase_sparql_string, parse_all=True)
        if parsed_sparql[2] != 'SELECT':
            pass  # error
        prefixes = parsed_sparql[1]
        if len(prefixes) > 0:
            prefixes_json = {}
            for prefix in prefixes:
                if prefix[0] != 'PREFIX':
                    pass  # error

                if len(list(prefix)) == 4:
                    prefixes_json[prefix[1]] = prefix[3][0]
                elif len(list(prefix)) == 3:
                    prefixes_json[''] = prefix[2][0]
                else:
                    pass  # error
            sparql_data['prefixes'] = prefixes_json
            working_prefixes = prefixes_json
        if len(parsed_sparql[3]) > 0 and (parsed_sparql[3][0] == 'DISTINCT'):
            sparql_data['distinct'] = True
        if len(parsed_sparql[4]) > 0:
            if parsed_sparql[4][0] == '*':
                sparql_data['variables'] = "*"
                pass  # TODO
            else:
                args = []
                for var in parsed_sparql[4]:
                    var_json = {'termType': 'Variable', 'value': var.replace('?', '')}
                    args.append(var_json)
                sparql_data['variables'] = args
        xxx0 = parsed_sparql[5]
        nnn0 = len(xxx0)
        yyy0 = xxx0[0][0]
        if len(xxx0) > 0:
            where_term = xxx0
            len_where_term = len(where_term)
            try:
                if len_where_term > 0:
                    xxx0 = where_term[0]
                    # xxx1 = where_term[1]
                    sparql_data['where'] = [create_where_clause_with_optional(where_term_0) for where_term_0 in where_term[0]]
                    if len_where_term > 1 and where_term[1][0].upper() == 'LIMIT':
                        sparql_data['limit'] = int(where_term[1][1])
            except Exception as e:
                # sparql_data['where'] = [create_where_clause_with_optional(where_term)]
                pass
        return sparql_data


def convert():
    # sparql_parse = SparqlParse()
    # Sample SPARQL query to parse
    # sample_query = """
    # PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    # PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    # PREFIX wd: <http://www.wikidata.org/entity/>
    # PREFIX wdt: <http://www.wikidata.org/prop/direct/>
    #
    # PREFIX ex: <http://example.com/ontology/>
    # PREFIX pred: <http://example.com/predicate/>
    # PREFIX country: <http://example.com/predicate/country>
    # PREFIX country_name: <http://example.com/predicate/country_name>
    # PREFIX country_description: <http://example.com/predicate/country_description>
    #
    # SELECT ?s ?hotel_name ?country_name
    # WHERE {
    #     ?s rdf:type ex:Hotel.
    #     ?s rdfs:label ?hotel_name.
    #     ?s pred:country ?country_id.
    #     ?country_id pred:country_name ?country_name.
    # }
    #
    # """

    sample_query = """
                PREFIX drugbank: <http://www4.wiwiss.fu-berlin.de/drugbank/resource/drugbank/> 
                PREFIX drugtype: <http://www4.wiwiss.fu-berlin.de/drugbank/resource/drugtype/>
                PREFIX kegg: <http://bio2rdf.org/ns/kegg#>
                PREFIX chebi: <http://bio2rdf.org/ns/bio2rdf#>
                PREFIX purl: <http://purl.org/dc/elements/1.1/>
                SELECT distinct ?drug	?drugDesc ?molecularWeightAverage 	?compound   ?ReactionTitle    ?ChemicalEquation 
                WHERE
                {
                ?drug 			drugbank:description 	 ?drugDesc .
                ?drug 			drugbank:drugType 	 drugtype:smallMolecule .
                ?drug 	     drugbank:keggCompoundId ?compound. 
                ?enzyme 		kegg:xSubstrate 	?compound .
                ?Chemicalreaction 	kegg:xEnzyme 		?enzyme .
                ?Chemicalreaction	kegg:equation 		?ChemicalEquation .
                ?Chemicalreaction 	purl:title 		?ReactionTitle 
                OPTIONAL 
                    { 
                        ?drug drugbank:molecularWeightAverage ?molecularWeightAverage.
                        FILTER (?molecularWeightAverage > 114) 
                    }
                }
                Limit 1000
                """
    # sample_query = """
    # SELECT ?name
    # WHERE {
    #   ?person <http://xmlns.com/foaf/0.1/name> ?name .
    # }
    # """
    # sample_query = """
    # SELECT ?name
    # WHERE {
    #   <http://xmlns.com/foaf/0.1/person> <http://xmlns.com/foaf/0.1/name> <http://xmlns.com/foaf/0.1/name> .
    # }
    # """
    # sample_query = """
    # SELECT ?name
    # WHERE {
    #  ?a <http://xmlns.com/foaf/0.1/name> ?c
    # }
    # """

    # Parse the sample query
    # result = query.parseString(sample_query)
    result = sparql_parse.query.parse_string(sample_query, parse_all=True)
    # Print the parsed structure
    print(result.dump())
    result = sparql_parse.convert_sparql(sample_query)

    pass


def compare():
    def sparql_read(file_path):
        with open(file_path, 'r') as input_file:
            sparql_string = input_file.read()
            return sparql_string

    def json_read(file_path):
        with open(file_path, 'r') as input_file:
            json_data = json.load(input_file)
            return json_data

    def compare_objects(object1, object2):
        try:
            if type(object1) == dict:
                if type(object2) == dict:
                    for key, element1 in object1.items():
                        try:
                            if key == 'subject' and element1['termType'] == 'BlankNode':
                                element2 = object2[key]
                                if element2['termType'] == 'BlankNode':
                                    return True
                                else:
                                    return False
                        except:
                            pass
                        element2 = object2[key]
                        result = compare_objects(element1, element2)
                        if not result:
                            return False
                else:
                    return False
            elif type(object1) == list:
                if type(object2) == list:
                    if len(object1) != len(object2):
                        return False
                    else:
                        for element1, element2 in zip(object1, object2):
                            result = compare_objects(element1, element2)
                            if not result:
                                return False
                else:
                    return False
            else:
                if object1 == object2:
                    return True
                else:
                    return False
            pass
        except KeyError:
            return False
        return True

    root = '../data'
    datasets = os.listdir(root)
    for dataset in datasets:
        if dataset != 'book20230728':  # debug
            # continue  # debug
            pass  # debug
        print('dataset: ', dataset)
        folders = os.listdir(root + '/' + dataset)
        for folder in folders:
            if folder == 'query':
                queries = os.listdir(root + '/' + dataset + '/' + folder)
                for query in queries:
                    if query.endswith('.txt'):
                        # if query != 'aaa.txt':
                        if query != '3_q1.txt':
                            continue
                            pass
                        if query == 'q1.txt':
                            # continue
                            pass
                        print('  query: ', query)
                        sparql_string = sparql_read(root + '/' + dataset + '/' + folder + '/' + query)
                        json_data = json_read(
                            root + '/' + dataset + '/' + folder + '/' + query.replace('.txt', '.json'))
                        sparql_data = sparql_parse.convert_sparql(sparql_string)
                        result1 = compare_objects(sparql_data, json_data)
                        result2 = compare_objects(json_data, sparql_data)
                        if not result1 or not result2:
                            pass
                        pass
    pass


class TestSparqlParse:  # not used
    def __init__(self):
        IRIREF = Group(Suppress('<') + Word(alphas, alphanums + '_' + '-' + '/' + ':' + '#' + '.') + Suppress('>'))

        VAR1 = Combine(Literal('?') + Word(alphanums + '_'))
        VAR2 = Combine(Literal('$') + Word(alphanums + '_'))
        var = VAR1 | VAR2

        # Define prefixes and base declarations
        BASE = Keyword("BASE")
        PREFIX = Keyword("PREFIX")
        # IRIREF = quotedString
        PNAME_NS = Word(alphas, alphanums + '_' + '#') + Literal(':') | Literal('') + Literal(':')  # ends with :
        prefixDecl = Group(PREFIX + PNAME_NS + IRIREF)
        baseDecl = Group(BASE + IRIREF)

        # Define keywords
        SELECT = Keyword("SELECT")
        DISTINCT = Keyword("DISTINCT")
        WHERE = Keyword("WHERE")
        FROM = Keyword("FROM")
        UNION = Keyword("UNION")  # 2024/6/24
        OPTIONAL = Keyword("OPTIONAL")  # 2024/7/1
        NAMED = Keyword("NAMED")
        LIMIT = Keyword("LIMIT")  # | Keyword("Limit")  # 2024/7/1
        OFFSET = Keyword("OFFSET")
        FILTER = Keyword("FILTER")
        STR = Keyword("STR")
        ORDER = Keyword("ORDER")
        BY = Keyword("BY")

        # Define basic RDF elements
        # rdfLiteral = quotedString | sglQuotedString | dblQuotedString | quoted_string | sgl_quoted_string | dbl_quoted_string
        rdfLiteral = quotedString
        # rdfLiteral = Word(alphanums + ' ' + '_' + '-' + '/' + ':' + '#' + '.' + '"' + "'")
        integer = Word(nums)
        numericLiteral = integer
        booleanLiteral = Keyword("true") | Keyword("false")
        literal = rdfLiteral | numericLiteral | booleanLiteral

        # iri = IRIREF | Combine(PNAME_NS + Word(alphanums + '_'))
        iri = IRIREF | Group(PNAME_NS + Word(alphanums + '_')) | Group(PNAME_NS)
        blankNode = Combine('_:' + Word(alphanums + '_')) | Group(Suppress('[') + Suppress(']'))
        # collection = Forward()
        # object_ = var | iri | literal | blankNode | collection
        object_ = var | iri | literal | blankNode

        subject = var | iri | blankNode  # | collection
        verb = var | iri | Keyword("a")  # predicate
        # objectList = Group(delimitedList(object_))
        objectList = object_  # 2024/7/3
        predicateObjectList = Group(Group(verb + objectList) + ZeroOrMore(Suppress(";") + Group(verb + objectList)))

        # triples and triples block
        triplesBlock = Group(subject + predicateObjectList) | Group(Suppress('[') + predicateObjectList + Suppress(']'))
        triplesBlockList = Group(triplesBlock + ZeroOrMore(Suppress(".") + ZeroOrMore(triplesBlock)))
        datatype = Suppress('^^') + Group(PNAME_NS + Word(alphanums + '_'))
        factor = (var | iri
                  | Group('LANG' + Suppress('(') + var + Suppress(')'))
                  | Group(STR + Suppress('(') + var + Suppress(')'))
                  | Group(literal + Optional(datatype)))
        expression = infixNotation(factor,
                                   [
                                       (oneOf("!"), 1, opAssoc.RIGHT),
                                       (oneOf("+ -"), 1, opAssoc.RIGHT),  # 符号は最優先。
                                       (oneOf("* /"), 2, opAssoc.LEFT),  # 掛け算割り算は足し算引き算より優先
                                       (oneOf("+ -"), 2, opAssoc.LEFT),
                                       (oneOf("= != > >= < <="), 2, opAssoc.LEFT),
                                       (oneOf("&& ||"), 2, opAssoc.LEFT),
                                   ]
                                   )
        filter = Group(FILTER + Suppress('(') + OneOrMore(expression) + Suppress(')'))

        triplesBlockListWithZeroOrMoreFilter = Group(triplesBlockList) + ZeroOrMore(filter)
        optionalExpression = Group(OPTIONAL + Suppress("{") + triplesBlockListWithZeroOrMoreFilter + Suppress("}"))
        basicGroupGraphPattern = Group(triplesBlockListWithZeroOrMoreFilter
                                             + ZeroOrMore(optionalExpression))

        groupGraphPattern = Group(basicGroupGraphPattern) | Suppress("{") + basicGroupGraphPattern \
                            + OneOrMore(Suppress(UNION) + basicGroupGraphPattern) + Suppress("}")

        whereClause = Suppress(Optional(WHERE)) + Suppress("{") + groupGraphPattern + Suppress("}")

        # Define the query structure
        limitExpression = Group(LIMIT + Word(nums))
        orderbyExpression = Group(ORDER + BY + Suppress("(") + VAR1 + Suppress(")"))
        selectQuery = SELECT + Group(Optional(DISTINCT)) + Group(OneOrMore(var) | "*") + whereClause + ZeroOrMore(
            limitExpression | orderbyExpression)

        # Define the full query structure with prologue
        self.query = Group(Optional(baseDecl)) + Group(ZeroOrMore(prefixDecl)) + selectQuery
        # IRIREF = Group(Suppress('<') + Word(alphas, alphanums + '_' + '-' + '/' + ':' + '#' + '.') + Suppress('>'))
        # VAR1 = Combine(Literal('?') + Word(alphanums + '_'))
        # VAR2 = Combine(Literal('$') + Word(alphanums + '_'))
        # var = VAR1 | VAR2
        # PNAME_NS = Word(alphas, alphanums + '_' + '#') + Literal(':') | Literal('') + Literal(':')  # ends with :
        text = Word(alphanums + '?')
        # rdfLiteral = quotedString
        # integer = Word(nums)
        # numericLiteral = integer
        # booleanLiteral = Keyword("true") | Keyword("false")
        # literal = rdfLiteral | numericLiteral | booleanLiteral
        # literal = OneOrMore(quoted_string | text)
        # literal = "'"+text+"'"
        # iri = IRIREF | Group(PNAME_NS + Word(alphanums + '_')) | Group(PNAME_NS)
        # object_ = var | iri | literal
        # verb = var | iri | Keyword("a")  # predicate
        # self.query = Keyword('SELECT') + 'DISTINCT' + '*' + 'WHERE' + '{' + OneOrMore(verb) + object_ + '.' + '}'


def parse_test():
    # test_sparql_query_parse = TestSparqlParse()
    test_sparql_query_parse = SparqlParse()
    query_string = """
    SELECT $drug $transform $mass WHERE {  
        $drug <http://www4.wiwiss.fu-berlin.de/drugbank/resource/drugbank/affectedOrganism>  'Humans and other mammals'.
        $drug <http://www4.wiwiss.fu-berlin.de/drugbank/resource/drugbank/casRegistryNumber> $cas .
        $keggDrug <http://bio2rdf.org/ns/bio2rdf#xRef> $cas .
        $keggDrug <http://bio2rdf.org/ns/bio2rdf#mass> $mass .	 
        OPTIONAL { $drug <http://www4.wiwiss.fu-berlin.de/drugbank/resource/drugbank/biotransformation> $transform . } 
    }
    """
    # xxx = test_sparql_query_parse.query.parse_string("?locationName a 'Islamic Republic of Afghanistan'", parse_all=True)
    xxx = test_sparql_query_parse.query.parse_string(query_string, parse_all=True)
    print(xxx)


if __name__ == '__main__':
    sparql_parse = SparqlParse()
    # convert()
    # compare()
    parse_test()
