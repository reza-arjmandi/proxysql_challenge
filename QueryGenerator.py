import random

class QueryGenerator:

    def generate(self, number_of_queries=1000000):
        queries_file_name = "queries.sql"
        with open(queries_file_name, "w") as queries_file:
            for i in range(number_of_queries):
                queries_file.write(f"/* {random. randint(0,200):03} */ select 'test' from dual;\n")
        return queries_file_name
