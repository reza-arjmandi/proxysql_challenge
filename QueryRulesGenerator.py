class QueryRulesGenerator:

    def __make_query_file_name__(self, with_FLAGIN_FLAGOUT, no_backend):
        query_file_name = "query_rules_" 
        query_file_name += "with_FLAGIN_FLAGOUT_" if with_FLAGIN_FLAGOUT else "without_FLAGIN_FLAGOUT_"
        query_file_name += "without_backend" if no_backend else "with_backend"
        query_file_name += ".sql"
        return query_file_name

    def __generate_query_rules__(self, number_of_shards, query_file_name, no_backend):
        with open(query_file_name, "w") as query_file:
            query_file.write("delete from mysql_query_rules;\n")
            for i in range(number_of_shards):
                destination_hostgroup = 1 if no_backend else 0
                ok_msg = f'"Shard {i:03}"' if no_backend else 'NULL'
                query_file.write(f"insert into mysql_query_rules (active, match_pattern, apply, destination_hostgroup, OK_msg) values (1, '\/\* {i:03}', 1, {destination_hostgroup}, {ok_msg});\n")
            query_file.write("LOAD MYSQL QUERY RULES TO RUNTIME;\n")

    def __make_leaf__(self, query_file, _range, flag_in, flag_out, ok_msg, destination_hostgroup):
        query_file.write(f"insert into mysql_query_rules (active,match_pattern,flagIN,flagOUT,apply,destination_hostgroup, OK_msg) values (1,'\/\* [{_range[0]}-{_range[1]}]',{flag_in},{flag_out},0,{destination_hostgroup}, {ok_msg});\n")
        query_file.write(f"insert into mysql_query_rules (active,match_pattern,flagIN,flagOUT,apply,destination_hostgroup, OK_msg) values (1,'\/\* {_range[0]}' ,{flag_in}, 0,1, {destination_hostgroup}, {ok_msg});\n")
        query_file.write(f"insert into mysql_query_rules (active,match_pattern,flagIN,flagOUT,apply,destination_hostgroup, OK_msg) values (1,'\/\* {_range[1]}' ,{flag_in}, 0,1, {destination_hostgroup}, {ok_msg});\n")

    def __make_node__(self, query_file, _range, flag_in, flag_out, height, ok_msg, destination_hostgroup):
        self.__make_leaf__(query_file, _range, flag_in, flag_out, ok_msg, destination_hostgroup)
        if height == 0:
            query_file.write(f"insert into mysql_query_rules (active,match_pattern,flagIN,flagOUT,apply,destination_hostgroup, OK_msg) values (1,'\/\* {_range[1] + 1}' , {flag_in}, 0,1, {destination_hostgroup}, {ok_msg});\n")
            query_file.write(f"insert into mysql_query_rules (active,match_pattern,flagIN,flagOUT,apply,destination_hostgroup, OK_msg) values (1,'\/\* {_range[1] + 2}' , {flag_in}, 0,1, {destination_hostgroup}, {ok_msg});\n")
            return _range[1] + 2

        for i in range(height):
            _range = [_range[1] + 1, _range[1] + 2]
            return self.__make_node__(query_file, _range, flag_in, flag_out, height - 1, ok_msg, destination_hostgroup)


    def __generate_FALGIN_FLAGOUT_query_rules__(self, number_of_shards, query_file_name, no_backend):
        _range = [0, 1]
        height = 0
        flag_in = 0
        flag_out = 1
        ok_msg = '""' if no_backend else "NULL"
        destination_hostgroup = "NULL" if no_backend else 0
        with open(query_file_name, "w") as query_file:
            query_file.write("delete from mysql_query_rules;\n")
            while _range[1] <  number_of_shards:
                _range[1] = self.__make_node__(query_file, _range, flag_in, flag_out, height, ok_msg, destination_hostgroup)
                height += 1
                flag_in = flag_out
                flag_out += 1
            query_file.write("LOAD MYSQL QUERY RULES TO RUNTIME;\n")

    def generate(self, number_of_shards=200, with_FLAGIN_FLAGOUT=False, no_backend=False):
        query_file_name = self.__make_query_file_name__(with_FLAGIN_FLAGOUT, no_backend) 
        if not with_FLAGIN_FLAGOUT:
            self.__generate_query_rules__(number_of_shards, query_file_name, no_backend)
        else:
            self.__generate_FALGIN_FLAGOUT_query_rules__(number_of_shards, query_file_name, no_backend)
        return query_file_name

if __name__ == "__main__":
    query_rules_generator = QueryRulesGenerator()
    query_rules_generator.generate(with_FLAGIN_FLAGOUT=True)