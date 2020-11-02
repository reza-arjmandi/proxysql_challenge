import random
import math

class QueryGenerator:

    def __rand_exp_dist__(self):
        rand_number = math.trunc(random.expovariate(1.0))
        if rand_number >= 200:
            rand_number = 199
        return rand_number
    
    def __rand_norm_dist__(self):
        return random. randint(0,200)

    def generate(self, number_of_queries=1000000, distribution='normal'):
        queries_file_name = "queries.sql"
        with open(queries_file_name, "w") as queries_file:
            for i in range(number_of_queries):
                rand_number = None
                if distribution == 'normal':
                    rand_number = self.__rand_norm_dist__()
                elif distribution == 'exponential':
                    rand_number = self.__rand_exp_dist__()
                queries_file.write(
                    f"/* {rand_number:03} */ \
select 'test' from dual;\n")
        return queries_file_name
