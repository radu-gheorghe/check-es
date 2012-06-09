h1. check-es

h2. Nagios/Shinken plugins for checking out on Elasticsearch

For now there are two of them:
* check_es_insert.py - gives you the number of new documents indexed per second
* check_es_docs.py - gives the total number of documents

The second depends on the first, so you need to install both (in the same directory) if you want to use the second only.

h2. Installation

* Copy the plugins in your Nagios plugins directory (usually /usr/lib/nagios/plugins)
* Make sure they can be executed by whatever runs them (Nagios/Shinken/NRPE)

h3. For using the plugin from Shinken directly (I bet it's the same with Nagios)

* edit /etc/shinken/commands.cfg and add something like this:

<pre>define command{
  command_name    check_es_docs
  command_line    /usr/local/shinken/libexec/check_ping -w 5000000 -c 10000000 -a elasticserver:9200
}</pre>

* edit the host configuration file for the host you want to monitor (eg: /etc/shinken/hosts/localhost.cfg), and add a service like this:

<pre>define service{
  host_name    linuxbox
  service_description    TotalESDocuments
  check_command    check_es_docs
  #other options, if you want
}</pre>

* restart Nagios/Shinken and it should work

h3. For running the plugin remotely via NRPE

* define the command in NRPE's config (eg: make a new file /etc/nagios/nrpe.d/check_es.cfg and make sure it's readable by nagios:nagios), that looks something like this:

<pre>command[check_es_docs]=/usr/lib/nagios/plugins/check_es_docs -w 5000000 -c 10000000</pre>

* restart NRPE server

* edit the host configuration file for the host you want to monitor (eg: /etc/shinken/hosts/localhost.cfg), and add a service like this:

<pre>define service{
  host_name    linuxbox
  service_description    TotalESDocuments
  check_command    check_nrpe!check_es_docs
  #other options, if you want
}</pre>

* restart Nagios/Shinken and it should work

h2. Command-line arguments

Run the plugins with <pre>--help</pre> for more information. But the idea is:
-c for the Critical value
-w for the Warning value
-a for the address of the Elasticsearch server to check on (host:port)
-f for the file to store previous results on (check_es_insert only)