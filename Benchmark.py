import subprocess
import re

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
        
    def run_scenarios(self, FLAGIN_FLAGOUT, no_backend):
        query_rules_file = self.query_rules_generator.generate(with_FLAGIN_FLAGOUT = FLAGIN_FLAGOUT, no_backend=no_backend)

        proxysql_process_command = f'mysql -u {self.proxysql_user} -p{self.proxysql_password} -h {self.host} -P{self.proxysql_admin_port} < {query_rules_file}'
        proxysql_process = subprocess.Popen(proxysql_process_command, shell=True)
        proxysql_process.wait()

        queries_file = self.query_generator.generate()
        sqlslap_process_command = f'mysqlslap -u {self.mysql_user} -p{self.mysql_password} -h {self.host} -P{self.proxysql_interface_port} --create-schema=information_schema -c {self.number_of_connections} -q {queries_file}'
        sqlslap_process = subprocess.Popen(sqlslap_process_command, shell=True, stdout=subprocess.PIPE)

        for line in sqlslap_process.stdout.readlines():
            self.__print_line__(str(line))

        sqlslap_process.wait()


if __name__ == "__main__":
    query_generator = QueryGenerator()
    query_rules_generator = QueryRulesGenerator()
    benchmark = Benchmark(query_generator, query_rules_generator)

    print('******************************************************************')
    print('query rules without flagIN and flagOUT and with backend server')
    print('******************************************************************')
    benchmark.run_scenarios(FLAGIN_FLAGOUT = False, no_backend=False)
    print('******************************************************************')
    print('query rules with flagIN and flagOUT and with backend server')
    print('******************************************************************')
    benchmark.run_scenarios(FLAGIN_FLAGOUT = True, no_backend=False)

    print('******************************************************************')
    print('query rules without flagIN and flagOUT and without backend server')
    print('******************************************************************')
    benchmark.run_scenarios(FLAGIN_FLAGOUT = False, no_backend=True)
    print('******************************************************************')
    print('query rules with flagIN and flagOUT and without backend server')
    print('******************************************************************')
    benchmark.run_scenarios(FLAGIN_FLAGOUT = True, no_backend=True)
