import math

class QueryRulesGenerator:

    def __make_query_file_name__(self, with_FLAGIN_FLAGOUT, no_backend, without_query_rules):
        query_file_name = "query_rules_" 
        if not without_query_rules:
            query_file_name += "with_FLAGIN_FLAGOUT_" if with_FLAGIN_FLAGOUT else "without_FLAGIN_FLAGOUT_"
            query_file_name += "without_backend" if no_backend else "with_backend"
        else:
            query_file_name += "with_query_rules"
        query_file_name += ".sql"
        return query_file_name

    def __generate_query_rules__(self, number_of_shards, query_file, no_backend):
        columns = "(active, match_pattern, apply, destination_hostgroup, OK_msg)"
        destination_hostgroup = 1
        ok_msg = f'""' if no_backend else 'NULL'

        for i in range(number_of_shards):
            values = f"values (1, '\/\* {i:03}', 1, {destination_hostgroup}, {ok_msg})"
            query_file.write(f"insert into mysql_query_rules {columns} {values};\n")

    def __generate_delete_query_rules_script__(self, query_file_name):
        with open(query_file_name, "w") as query_file:
            query_file.write("delete from mysql_query_rules;\n")
            query_file.write("LOAD MYSQL QUERY RULES TO RUNTIME;\n")
            
    def __make_B_tree__(self, _range, query_file, ok_msg, destination_hostgroup, flag_in, flag_out):
        if _range[1] - _range[0] == 0:
            return

        columns = "(active,match_pattern,flagIN,flagOUT,apply,destination_hostgroup, OK_msg)"
        if _range[1] - _range[0] == 1:
            match_pattern = f"'\/\* {_range[0]}'"
            values = f"values (1, {match_pattern}, {flag_in}, 0,1, {destination_hostgroup}, {ok_msg})"
            query_file.write(f"insert into mysql_query_rules {columns} {values};\n")
            
            match_pattern = f"'\/\* {_range[1]}'"
            values = f"values (1, {match_pattern}, {flag_in}, 0,1, {destination_hostgroup}, {ok_msg})"
            query_file.write(f"insert into mysql_query_rules {columns} {values};\n")
            return
        
        match_pattern = f"'\/\* [{_range[0]}-{_range[1]}]'"
        values = f"values (1, {match_pattern}, {flag_in},{flag_out},0,{destination_hostgroup}, {ok_msg})"
        query_file.write(f"insert into mysql_query_rules {columns} {values};\n")
        self.__make_B_tree__([_range[0], math.floor((_range[0] + _range[1]) / 2)], query_file, ok_msg, destination_hostgroup, flag_out, flag_out+1)
        self.__make_B_tree__([math.floor((_range[0] + _range[1]) / 2) + 1, _range[1]], query_file, ok_msg, destination_hostgroup, flag_out, flag_out+1)

    def __generate_FALGIN_FLAGOUT_query_rules__(self, number_of_shards, query_file, no_backend):
        _range = [0, number_of_shards]
        flag_in = 0
        flag_out = 1
        ok_msg = '""' if no_backend else "NULL"
        destination_hostgroup = 1
        self.__make_B_tree__(_range, query_file, ok_msg, destination_hostgroup, flag_in, flag_out)

    def generate(self, number_of_shards=200, with_FLAGIN_FLAGOUT=False, no_backend=False, without_query_rules=False):
        query_file_name = self.__make_query_file_name__(with_FLAGIN_FLAGOUT, no_backend, without_query_rules) 

        with open(query_file_name, "w") as query_file:
            query_file.write("delete from mysql_query_rules;\n")

            if (not with_FLAGIN_FLAGOUT) and (not without_query_rules):
                self.__generate_query_rules__(number_of_shards, query_file, no_backend)
            elif with_FLAGIN_FLAGOUT and (not without_query_rules):
                self.__generate_FALGIN_FLAGOUT_query_rules__(number_of_shards, query_file, no_backend)

            query_file.write("LOAD MYSQL QUERY RULES TO RUNTIME;\n")
            
        return query_file_name
