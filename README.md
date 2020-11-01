# ProxySQL Benchmark

## Requirements
* Python 3
* dbdeployer
* ProxySQL
* mysql client
  
## Prepare

### Deploy MySQL Server

* dbdeployer downloads get-by-version 5.7 --newest
* dbdeployer unpack mysql-5.7.31-linux-glibc2.12-x86_64.tar.gz
* dbdeployer deploy replication 5.7.31 --read-only-slaves

Run the following command to see the sandboxe's ports:
* dbdeployer sandboxes  
output: rsandbox_5_7_31 : master-slave 5.7.31 [19832 19833 19834 ]
  
### Configure ProxySQL

* mysql -u admin -padmin -h 127.0.0.1 -P6032
* INSERT INTO mysql_servers(hostgroup_id,hostname,port) VALUES (1,'127.0.0.1',19832);
* INSERT INTO mysql_servers(hostgroup_id,hostname,port) VALUES (1,'127.0.0.1',19833);
* INSERT INTO mysql_servers(hostgroup_id,hostname,port) VALUES (1,'127.0.0.1',19834);
* UPDATE global_variables SET variable_value='msandbox' WHERE variable_name='mysql-monitor_username';
* UPDATE global_variables SET variable_value='msandbox' WHERE variable_name='mysql-monitor_password';
* UPDATE global_variables SET variable_value='2000' WHERE variable_name IN ('mysql-monitor_connect_interval','mysql-monitor_ping_interval','mysql-monitor_read_only_interval');
* INSERT INTO mysql_replication_hostgroups (writer_hostgroup,reader_hostgroup,comment) VALUES (1,2,'cluster1');
* INSERT INTO mysql_users(username,password,default_hostgroup) VALUES ('root','',1);
* INSERT INTO mysql_users(username,password,default_hostgroup) VALUES ('msandbox','msandbox',1);
* LOAD MYSQL VARIABLES TO RUNTIME;
* LOAD MYSQL SERVERS TO RUNTIME;
* LOAD MYSQL USERS TO RUNTIME;
* SAVE MYSQL SERVERS TO DISK;
* SAVE MYSQL USERS TO DISK;
* SAVE MYSQL VARIABLES TO DISK;

### Run Benchmark

* python3 Benchmark.py

## Conclusion

* The result that I've achieved:

* Query rules without flagIN and flagOUT and with backend server:
1. Average number of seconds to run all queries: 144.223 seconds
2. Minimum number of seconds to run all queries: 144.223 seconds
3. Maximum number of seconds to run all queries: 144.223 seconds

* Query rules with flagIN and flagOUT and with backend server:
1. Average number of seconds to run all queries: 77.044 seconds
2. Minimum number of seconds to run all queries: 77.044 seconds
3. Maximum number of seconds to run all queries: 77.044 seconds

* Query rules without flagIN and flagOUT and without backend server: 
1. Average number of seconds to run all queries: 47.922 seconds
2. Minimum number of seconds to run all queries: 47.922 seconds
3. Maximum number of seconds to run all queries: 47.922 seconds

* Query rules with flagIN and flagOUT and without backend server: 
1. Average number of seconds to run all queries: 23.011 seconds
2. Minimum number of seconds to run all queries: 23.011 seconds
3. Minimum number of seconds to run all queries: 23.011 seconds

* Without query rules:
1. Average number of seconds to run all queries: 77.145 seconds
2. Minimum number of seconds to run all queries: 77.145 seconds
3. Maximum number of seconds to run all queries: 77.145 seconds
