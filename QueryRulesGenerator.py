import math

class QueryRulesGenerator:

    def __init__(self):
        self.insert_statement = "insert into mysql_query_rules"

    def __make_query_file_name__(
        self, 
        with_FLAGIN_FLAGOUT, 
        no_backend, 
        without_query_rules):

        query_file_name = "query_rules_" 
        if not without_query_rules:
            query_file_name +=\
                "with_FLAGIN_FLAGOUT_" \
                    if with_FLAGIN_FLAGOUT \
                        else "without_FLAGIN_FLAGOUT_"
            query_file_name +=\
                "without_backend" \
                    if no_backend \
                        else "with_backend"
        else:
            query_file_name = "without_query_rules"
        query_file_name += ".sql"
        return query_file_name

    def __generate_query_rules__(
        self, 
        number_of_shards, 
        query_file, 
        no_backend):

        columns =\
            "(active, \
match_pattern, \
apply, \
destination_hostgroup, \
OK_msg)"
        destination_hostgroup = 1
        ok_msg = f'""' if no_backend else 'NULL'

        for i in range(number_of_shards):
            active = 1
            match_pattern = f"'\/\* {i:03}'"
            apply = 1
            values =\
                f"values (\
{active}, \
{match_pattern}, \
{apply}, \
{destination_hostgroup}, \
{ok_msg}\
)"
            query_file.write(f"{self.insert_statement} {columns} {values};\n")

    def __make_B_tree__(
        self, 
        _range, 
        query_file, 
        ok_msg, 
        destination_hostgroup, 
        flag_in, 
        flag_out):

        if _range[1] - _range[0] == 0:
            return

        columns = "(active, \
match_pattern, \
flagIN, \
flagOUT, \
apply, \
destination_hostgroup, \
OK_msg)"
        active = 1
        
        if _range[1] - _range[0] == 1:
            match_pattern = f"'\/\* {_range[0]}'"
            flag_out_ = 0
            apply = 1
            values = f"values (\
{active}, \
{match_pattern}, \
{flag_in}, \
{flag_out_}, \
{apply}, \
{destination_hostgroup}, \
{ok_msg}\
)"
            query_file.write(f"{self.insert_statement} {columns} {values};\n")
            
            match_pattern = f"'\/\* {_range[1]}'"
            values = f"values (\
{active}, \
{match_pattern}, \
{flag_in}, \
{flag_out_}, \
{apply}, \
{destination_hostgroup}, \
{ok_msg})"
            query_file.write(f"{self.insert_statement} {columns} {values};\n")
            return
        
        match_pattern = f"'\/\* [{_range[0]}-{_range[1]}]'"
        apply = 1
        values = f"values (\
{active}, \
{match_pattern}, \
{flag_in}, \
{flag_out}, \
{apply}, \
{destination_hostgroup}, \
{ok_msg}\
)"
        query_file.write(f"{self.insert_statement} {columns} {values};\n")
        range_down = [_range[0], math.floor((_range[0] + _range[1]) / 2)]
        self.__make_B_tree__(
            range_down, 
            query_file, 
            ok_msg, 
            destination_hostgroup, 
            flag_out, 
            flag_out+1)
        range_up = [math.floor((_range[0] + _range[1]) / 2) + 1, _range[1]]
        self.__make_B_tree__(
            range_up, 
            query_file, 
            ok_msg, 
            destination_hostgroup, 
            flag_out, 
            flag_out+1)

    def __generate_FALGIN_FLAGOUT_query_rules__(
        self, 
        number_of_shards, 
        query_file, 
        no_backend):

        _range = [0, number_of_shards]
        flag_in = 0
        flag_out = 1
        ok_msg = '""' if no_backend else "NULL"
        destination_hostgroup = 1
        self.__make_B_tree__(
            _range, 
            query_file, 
            ok_msg, 
            destination_hostgroup, 
            flag_in, 
            flag_out)

    def generate(
        self, 
        number_of_shards=200, 
        with_FLAGIN_FLAGOUT=False, 
        no_backend=False, 
        without_query_rules=False):

        query_file_name = self.__make_query_file_name__(
            with_FLAGIN_FLAGOUT, no_backend, without_query_rules) 

        with open(query_file_name, "w") as query_file:
            query_file.write("delete from mysql_query_rules;\n")

            if (not with_FLAGIN_FLAGOUT) and (not without_query_rules):
                self.__generate_query_rules__(
                    number_of_shards, query_file, no_backend)
            elif with_FLAGIN_FLAGOUT and (not without_query_rules):
                self.__generate_FALGIN_FLAGOUT_query_rules__(
                    number_of_shards, query_file, no_backend)

            query_file.write("LOAD MYSQL QUERY RULES TO RUNTIME;\n")
            
        return query_file_name
