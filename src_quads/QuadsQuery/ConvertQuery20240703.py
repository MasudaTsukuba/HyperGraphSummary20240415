"""
ConvertQuery20240703.py
Called from QuadQuery20240624.py
2024/7/3, T. Masuda
Amagasa Laboratory, University of Tsukuba
"""

from src_quads.QuadsQuery.SparqlParse20240624 import SparqlParse  # call SparqlParse


class ConvertQuery:
    def convert_query(self, query_string):
        sparql_parse = SparqlParse()  # create an instance of SparqlParse()

        def convert_term(triple_term):
            triple_term_return = ''
            if type(triple_term) == str:
                triple_term_return = triple_term
            else:
                try:
                    if triple_term['termType'] == 'Variable':
                        triple_term_return = f"?{triple_term['value']}"
                    elif triple_term['termType'] == 'NamedNode':
                        triple_term_return = f"<{triple_term['value']}>"
                    elif triple_term['termType'] == 'Literal':
                        triple_term_return = f"{triple_term['value']}"
                    else:
                        pass  # error
                except Exception as e:
                    pass
            return triple_term_return

        def convert_authority(so):
            converted_so = convert_term(so)
            if so['termType'] == 'NamedNode':
                replaced_so = converted_so.replace('://', ':__')
                converted_so = replaced_so.split('/')[0].replace(':__', '://')
                if not converted_so.endswith('>'):
                    converted_so += '>'
            return converted_so

        def convert_arg(arg_clause):
            arg_term = ''
            if arg_clause['termType'] == 'Variable':
                return f"?{arg_clause['value']}"
            elif arg_clause['termType'] == 'Literal':
                datatype_term = ''
                try:
                    datatype_term = f"^^<{arg_clause['datatype']['value']}>"
                except Exception as e:
                    pass
                arg_term = f'"{arg_clause["value"]}"{datatype_term}'
                pass
            return arg_term

        def convert_filter(filter_clause):
            filter_term = ''
            if filter_clause['type'] == 'operation':
                operator = filter_clause['operator']
                args = filter_clause['args']
                filter_term += f"{convert_arg(args[0])} {operator} {convert_arg(args[1])}"
            else:
                pass  # unexpected
            pass
            return filter_term

        def convert_where(where_clause):
            where_term = ''
            for where_clause_component in where_clause:
                if where_clause_component['type'] == 'bgp':
                    for triple in where_clause_component['value']:
                        subj = convert_authority(triple['subject'])
                        pred = convert_term(triple['predicate'])
                        obje = convert_authority(triple['object'])
                        where_term += f"GRAPH ?graph{str(SparqlParse.graph_index)} \n{{ {subj} {pred} {obje} . }} \n"
                        SparqlParse.graph_index += 1
                elif where_clause_component['type'] == 'filter':
                    where_term += f"FILTER ({convert_filter(where_clause_component['value'])})"
            return where_term

        def convert_where_optional(where_clause_optional):
            where_term_optional = ''
            for where_clause_component in where_clause_optional:
                if where_clause_component['type'] == 'mandatory':
                    where_term_optional += convert_where(where_clause_component['value'])
                elif where_clause_component['type'] == 'optional':
                    where_term_optional += f"OPTIONAL {{ {convert_where(where_clause_component['value'])} }} "
            return where_term_optional

        try:  # start of convert_query
            sparql_data = sparql_parse.convert_sparql(query_string)

            converted_query = ''
            if sparql_data['queryType'] == 'SELECT':
                converted_query += 'SELECT '
                # for variable in sparql_data['variables']:
                #     converted_query += f"?{variable['value']} "
                converted_query += '* '
                converted_query += '\nWHERE { \n'
                if len(sparql_data['where']) == 1:  # without 'UNION'
                    sparql_data_where = sparql_data['where'][0]
                    converted_query += convert_where_optional(sparql_data_where)
                    pass
                else:  # with 'UNION'
                    sparql_data_where_list = []
                    for sparql_data_where in sparql_data['where']:
                        sparql_data_where_list.append(f"{{ \n{convert_where_optional(sparql_data_where)}}}" )
                        pass
                    converted_query += '\nUNION \n'.join(sparql_data_where_list)
                converted_query += '\n}'  # close WHERE
                pass
            else:
                pass  # not yet implemented
        except Exception as e:
            print(e)
            converted_query = ''
            pass

        return converted_query
