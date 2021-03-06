#!/usr/bin/env python
"""
Licensed to the Apache Software Foundation (ASF) under one
or more contributor license agreements.  See the NOTICE file
distributed with this work for additional information
regarding copyright ownership.  The ASF licenses this file
to you under the Apache License, Version 2.0 (the
"License"); you may not use this file except in compliance
with the License.  You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.

"""

from ambari_commons import OSCheck

from resource_management.libraries.functions import conf_select
from resource_management.libraries.functions import stack_select
from resource_management.libraries.functions import format
from resource_management.libraries.functions.default import default
from resource_management.libraries.functions import get_kinit_path
from resource_management.libraries.script.script import Script

# a map of the Ambari role to the component name
# for use with /usr/iop/current/<component>
SERVER_ROLE_DIRECTORY_MAP = {
  'HIVE_METASTORE' : 'hive-metastore',
  'HIVE_SERVER' : 'hive-server2',
  'WEBHCAT_SERVER' : 'hive-webhcat',
  'HIVE_CLIENT' : 'hive-client',
  'HCAT' : 'hive-client'
}

component_directory = Script.get_component_from_role(SERVER_ROLE_DIRECTORY_MAP, "HIVE_CLIENT")

config = Script.get_config()

hive_pid_dir = config['configurations']['hive-env']['hive_pid_dir']
hive_pid = 'hive-server.pid'

hive_metastore_pid = 'hive.pid'

hcat_pid_dir = config['configurations']['hive-env']['hcat_pid_dir'] #hcat_pid_dir
webhcat_pid_file = format('{hcat_pid_dir}/webhcat.pid')

process_name = 'mysqld'
if OSCheck.is_suse_family() or OSCheck.is_ubuntu_family():
  daemon_name = 'mysql'
elif OSCheck.is_redhat_family() and int(OSCheck.get_os_major_version()) >= 7:
  daemon_name = 'mariadb'
else:
  daemon_name = 'mysqld'

# Security related/required params
hostname = config['hostname']
security_enabled = config['configurations']['cluster-env']['security_enabled']
kinit_path_local = get_kinit_path(default('/configurations/kerberos-env/executable_search_paths', None))
tmp_dir = Script.get_tmp_dir()
hdfs_user = config['configurations']['hadoop-env']['hdfs_user']
hive_user = config['configurations']['hive-env']['hive_user']
webhcat_user = config['configurations']['hive-env']['webhcat_user']

# default configuration directories
hadoop_conf_dir = conf_select.get_hadoop_conf_dir()
hadoop_bin_dir = stack_select.get_hadoop_dir("bin")
webhcat_conf_dir = '/etc/hive-webhcat/conf'
hive_etc_dir_prefix = "/etc/hive"
hive_conf_dir = "/etc/hive/conf"
hive_client_conf_dir = "/etc/hive/conf"

hive_server_conf_dir = "/etc/hive/conf.server"

if Script.is_stack_greater_or_equal("4.1.0.0"):
  webhcat_conf_dir = '/usr/iop/current/hive-webhcat/conf'
  hive_conf_dir = format("/usr/iop/current/{component_directory}/conf")
  hive_client_conf_dir = format("/usr/iop/current/{component_directory}/conf")
  hive_server_conf_dir = format("/usr/iop/current/{component_directory}/conf/conf.server")

hive_config_dir = hive_client_conf_dir
if 'role' in config and config['role'] in ["HIVE_SERVER", "HIVE_METASTORE"]:
  hive_config_dir = hive_server_conf_dir
