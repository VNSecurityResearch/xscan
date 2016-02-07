import multiprocessing
import sys, os, time, pickle

PROCNAME = "nmap"

def check_for_save():
    if os.path.exists('save'):
        save_state()

def test_network_wrapper():
    # usage:
    #     global counter = 0
    #    test_network_wrapper()
    global counter
    while(test_network()==False):
        if counter == 0:
            print 'script, you have Internet problem, saving the state of scan!'
            save_state_wo_exit()
            counter = counter + 1
        else:
            print 'script, '+ str(counter) + '. Internet problem still persisted!'
            time.sleep(5)
            counter = counter + 1
    
    if(counter!=0):
        print 'script, Internet problem has been solved, load the saved state, and resume'
        load_state()

def test_network():
    hostname = "google.com" #example
    response = os.system("ping -c 4 " + hostname + ' >/dev/null 2>/dev/null')

    #and then check the response...
    if response == 0:
        return True
    else:
        return False

def readInitIp(initfile):
    ipfile = open(initfile, 'r')
    lines = ipfile.readlines()
    for i in range(len(lines)):
        lines[i] = lines[i].strip()
    try:
        lines.remove('')
    except:
        print 'Well, you have no emty line'
    return lines

def nmapStartRunner(ip):
    
    
    outfile = ip.replace('/', '..')
    command = 'nmap -sV -O -Pn -o' + outfile + '.out ' + ip + ' >/dev/null 2>/dev/null'
    print 'script, Starting: '+ command
    os.system(command)

def nmapResumeRunner(ip):
    
    outfile = ip.replace('/', '..')
    command = 'nmap --resume '+ outfile + '.out' + ' >/dev/null 2>/dev/null'
    print 'script, Starting: '+ command
    os.system(command)

class state:
    def __init__(self, ips, running_ips, next_ips):
        self.ips = ips # list of ip(s) to scan
        self.running_ips = running_ips # list of ip(s), which is running
        self.next_ips = next_ips # index in list of ip(s)
    
def save_state():
    global ips, running_ips, next_ips, threads
    print 'script, you want to leave, I will try to save state'
    print 'script, killing all child-processes'

    for t in threads:
        t.terminate()

    os.system('killall nmap')
    

    time.sleep(0.25)
    sstate = state(ips, running_ips, next_ips)

    with open('state.picke', 'wb') as f:
        pickle.dump(sstate, f)

    print 'script, state.picke saved!'
    print 'script, killing myself and exit'
    os.system('kill $PPID')

def save_state_wo_exit():
    global ips, running_ips, next_ips, threads
    print 'script, saving state with out exit'
    print 'script, killing all child-processes'

    for t in threads:
        t.terminate()

    os.system('killall nmap')
    


    time.sleep(0.25)
    sstate = state(ips, running_ips, next_ips)

    with open('state.picke', 'wb') as f:
        pickle.dump(sstate, f)

    print 'script, state.picke saved!'


def load_state():
    global ips, running_ips, next_ips, threads
    print 'script, you want to resume, I will try to load saved state'
    with open('state.picke', 'rb') as f:
        sstate = pickle.load(f) 
    
    ips = sstate.ips
    running_ips = sstate.running_ips
    next_ips = sstate.next_ips

    # flush running_ips, threads before continue
    tmp_running_ips = running_ips
    running_ips = {}
    threads = []

    for v in tmp_running_ips.values():
        # check the number of line of output file, if it's less than, equal 1, treat as new scan
        vout = v.replace('/', '..') + '.out'
        with open(vout, 'r') as f:
            vlines = f.readlines()
            
        if vlines <=1:
            t = multiprocessing.Process(target = nmapStartRunner, args = (v,))
           
            t.start()
        else:
            t = multiprocessing.Process(target = nmapResumeRunner, args = (v,))
           
            t.start()
        threads.append(t) 

        running_ips[t.name] = v

    print 'script, threads after resumed: ' + str(threads)
    
def scan_it(max_thread):
    # if sys.argv[0] == start, new scan
    # if sys.argv[0] == resume, resume scan
    
    global ips, threads, running_ips, next_ips, counter


    if len(sys.argv) != 2:
        print 'script, You must provide an argument'
        exit(1)

    if sys.argv[1] == 'start':
        ips = readInitIp('init.ip')

        print "You have chosen 'start'"
        for i in range(max_thread):
            t = multiprocessing.Process(target = nmapStartRunner, args = (ips[i],))
           
            t.start()
            threads.append(t) 

            running_ips[t.name] = ips[i]

        print 'script, initial threads: ' + str(threads)
        next_ips = max_thread
    
    elif sys.argv[1] == 'resume':
        # do somethine here
        # load saved scan:
        # ips, list currently running thread - ips, next_ips
        tmp_running_ips = {}
        load_state()

    else:
        print sys.argv[1]
        print 'Please use start/resume'
        exit(1)

    while True:
        counter = 0
        test_network_wrapper()
        check_for_save()

        for k in range(len(threads)):
            if(threads[k].is_alive()==False):
                #del running_ips[str(threads[k])]
                print 'script, remove the thread "' + str(threads[k]) + '"'
                threads.remove(threads[k])
                print 'script, list of currently running threads after killed: ' + str(threads)
                break # if there is not this line, logic will failed on threads.remove(), the len of THREADS back to 1, while we have removed 1, but still want to remove at the index of 1 (meaning 2 elements)

        if len(threads) < max_thread:
            if next_ips < len(ips):
                print 'script, A thread of scan has finished, starting a new one'
                t = multiprocessing.Process(target = nmapStartRunner, args = (ips[next_ips],))
               
                t.start()
                next_ips = next_ips + 1
                threads.append(t)
                print 'script, thread after added new one: ' + str(threads)
            else:
                print 'script, We have iterate over all the init lines'
                break

    while True:
        counter = 0
        test_network_wrapper()
        check_for_save()

        for k in range(len(threads)):
            if(threads[k].is_alive()==False):
                threads.remove(threads[k])
                break # if there is not this line, logic will failed on threads.remove(), the len of THREADS back to 1, while we have removed 1, but
                # still want to remove at the index of 1 (meaning 2 elements)    
        time.sleep(5)        
        print 'The remainning thread run: ' + str(len(threads))
        if(len(threads)==0):
            print 'We have finished, get out!'
            exit(0)    

# global vars, need for handing saving state with signal
ips = []
next_ips = 0
running_ips = {}
processes = {}

threads = []
counter = 0

scan_it(3)
    
