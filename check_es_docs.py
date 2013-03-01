#!/usr/bin/python

import check_es_insert

###CONSTANTS###
OK=0
WARNING=1
CRITICAL=2
UNKNOWN=3
###END CONSTANTS###

def main():
    #get my command-line arguments
    cmdline = check_es_insert.getArgs('Nagios plugin for checking the total number of documents stored in Elasticsearch')
    #make a calculator
    my_calc = check_es_insert.Calculator(warn=cmdline['warning'],crit=cmdline['critical'],myfile=cmdline['file'],myaddress=cmdline['address'],index=cmdline['index'])
    #get the current number of documents from Elasticsearch
    (result,time) = my_calc.getCurrent()
    #if there's an error, exit with UNKNOWN
    if result == -1:
        check_es_insert.printer("Can't get number of documents from Elasticsearch")
        check_es_insert.exiter(UNKNOWN)
    else:
        #otherwise, thown in some nicely formatted text
        check_es_insert.printer("Total number of documents in Elasticsearch (index: %s) is %d | 'es_docs'=%d;%d;%d;;" % (cmdline['index'] if cmdline['index'] != '' else 'all', result,result,cmdline['warning'],cmdline['critical']))
        #and exit with the code returned by Calculator
        (text,exitcode)=my_calc.printandexit(result)
        check_es_insert.exiter(exitcode)

if __name__=="__main__":
    main()
