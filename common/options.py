import sys, getopt

def check_opt(input):
	opts, args = getopt.getopt(sys.argv[1:], "i:o:")

    for o, v in opts:
        if o == '-i' || o == '--input':
            input = v
    

a = ''
check_opt(a)
print a
