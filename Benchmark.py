import subprocess
import re
import os

from QueryGenerator import QueryGenerator
from QueryRulesGenerator import  QueryRulesGenerator

class Benchmark:

    def __init__(self, query_generator, query_rules_generator):
        self.query_generator = query_generator
        self.query_rules_generator = query_rules_generator
        self.mysql_user = 'msandbox'
        self.mysql_password = 'msandbox'
        self.proxysql_user = 'admin'
        self.proxysql_password = 'admin'
        self.proxysql_interface_port = 6033
        self.proxysql_admin_port = 6032
        self.number_of_connections = 4
        self.host = '127.0.0.1'

    def __print_line__(self, str):
        match_obj = re.match( r'^.*([AM].*): (.*) seconds.*$', str)
        if match_obj:
            print(f"{match_obj.group(1)}: {match_obj.group(2)} seconds")

    def __apply_query_rules_to_proxy_sql__(
        self, FLAGIN_FLAGOUT, no_backend, without_query_rules):

        query_rules_file = self.query_rules_generator.generate(
                with_FLAGIN_FLAGOUT = FLAGIN_FLAGOUT, 
                no_backend=no_backend, 
                without_query_rules = without_query_rules)
        proxysql_process_command =\
            f'mysql \
                -u {self.proxysql_user} \
                    -p{self.proxysql_password} \
                        -h {self.host} \
                            -P{self.proxysql_admin_port} \
                                < {query_rules_file}'
        FNULL = open(os.devnull, 'w')
        proxysql_process = subprocess.Popen(
            proxysql_process_command, 
            shell=True, 
            stderr=FNULL)
        proxysql_process.wait()

    def __load_tests__(self):
        queries_file = self.query_generator.generate()
        sqlslap_process_command =\
            f'mysqlslap \
                -u {self.mysql_user} \
                    -p{self.mysql_password} \
                        -h {self.host} \
                            -P{self.proxysql_interface_port} \
                                --create-schema=information_schema \
                                    -c {self.number_of_connections} \
                                        -q {queries_file}'
        FNULL = open(os.devnull, 'w')
        sqlslap_process = subprocess.Popen(
            sqlslap_process_command, 
            shell=True, 
            stdout=subprocess.PIPE, 
            stderr=FNULL)
        for line in sqlslap_process.stdout.readlines():
            self.__print_line__(str(line))
        sqlslap_process.wait()

    def run_scenarios(
        self, 
        FLAGIN_FLAGOUT=False, 
        no_backend=False, 
        without_query_rules=False):

        self.__apply_query_rules_to_proxy_sql__(
            FLAGIN_FLAGOUT, 
            no_backend, 
            without_query_rules)
        self.__load_tests__()

if __name__ == "__main__":
    query_generator = QueryGenerator()
    query_rules_generator = QueryRulesGenerator()
    benchmark = Benchmark(query_generator, query_rules_generator)

    print('******************************************************************')
    print('query rules without flagIN and flagOUT and with backend server')
    benchmark.run_scenarios(FLAGIN_FLAGOUT = False, no_backend=False)
    print('******************************************************************')
    print('query rules with flagIN and flagOUT and with backend server')
    benchmark.run_scenarios(FLAGIN_FLAGOUT = True, no_backend=False)

    print('******************************************************************')
    print('query rules without flagIN and flagOUT and without backend server')
    benchmark.run_scenarios(FLAGIN_FLAGOUT = False, no_backend=True)
    print('******************************************************************')
    print('query rules with flagIN and flagOUT and without backend server')
    benchmark.run_scenarios(FLAGIN_FLAGOUT = True, no_backend=True)

    print('******************************************************************')
    print('Without query rules')
    benchmark.run_scenarios(without_query_rules=True)