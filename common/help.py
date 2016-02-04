def print_help():
    print 'Usage: python xscan [options]'
    print ' '
    print 'Options:'
    print '\t-h, --help\t\tShow basic help message and exit'
    print '\t-i, --input\t\tNmap input file list, seperated by space (-iL option for Nmap)'
    print '\t-c, --count\t\tNumber of Nmap instance(s) to do scanning, default is 3'
 

def print_not_enough_mandatory_option():
    print 'xscan: error: missing mandatory option (-i, --input), use -h, --help for basic help'    


