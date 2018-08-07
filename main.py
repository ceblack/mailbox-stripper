import sys
import mailbox
import env
import time

RAW_EMAILS = []
FINISHED_EMAILS = []

MSG_COUNT = 0
START = time.time()

BAD_CHARS = env.BAD_CHARS
BAD_PREFIXES = env.BAD_PREFIXES
BAD_DOMAINS = env.BAD_DOMAINS

def readMbox(mboxPath):
    global RAW_EMAILS
    mbox = mailbox.mbox(mboxPath)

    for msg in mbox:
        try:
            stripEmails(msg)

        except Exception as e:
            print(str(e))

    RAW_EMAILS = list(set(RAW_EMAILS))

def stripEmails(msg):
    global RAW_EMAILS, MSG_COUNT
    MSG_COUNT += 1
    emails = []

    keys = list(msg.keys())

    if 'To' in keys:
        toAddrs = removeChars(msg['To']).split(',')
        emails += toAddrs

    if 'From' in keys:
        fromAddrs = removeChars(msg['From']).split(',')
        emails += fromAddrs

    if 'Cc' in keys:
        ccAddrs = removeChars(msg['Cc']).split(',')
        emails += ccAddrs

    if 'Bcc' in keys:
        bccAddrs = removeChars(msg['Bcc']).split(',')
        emails += bccAddrs

    emails = list(set(emails))
    RAW_EMAILS += emails

    if MSG_COUNT % 1000 == 0:
        RAW_EMAILS = list(set(RAW_EMAILS))

def removeBadElements():
    count = 0

    for email in RAW_EMAILS:
        name = ''
        addr = ''
        goodResult = True

        if '<' in email:
            name = removeErrantSpaces(email[:email.index('<')])
            addr = removeErrantSpaces(email[email.index('<') + 1:email.index('>')])

        else:
            addr = removeErrantSpaces(email)

        if '@' in addr:
            domain = addr[addr.index('@')+1:].lower()
            prefix = addr[:addr.index('@')].lower()

            for x in BAD_PREFIXES:
                if x in prefix:
                    goodResult = False

            for x in BAD_DOMAINS:
                if x in domain:
                    goodResult = False

        else:
            goodResult = False

        if goodResult:
            count += 1
            print(addr, count)
            writeRecord(name, addr)

def removeChars(x):
    for char in BAD_CHARS:
        x = x.replace(char, '')

    return(x)

def removeErrantSpaces(x):
    if len(x) > 1:
        while x[0] == ' ':
            if len(x) > 1:
                x = x[1:]

            else:
                return('')

        while x[-1] == ' ':
            if len(x) > 1:
                x = x[:-1]

            else:
                return(x)

        return(x)

    else:
        return('')

def writeRecord(name, addr):
    outString = name + '|' + addr + '\n'
    f = open(str(int(START)) + '.csv', 'a')
    f.write(outString)
    f.close()

def execute(mboxPath):
    readMbox(mboxPath)

    removeBadElements()

    runTime = time.time() - START
    avgTime = round(MSG_COUNT / runTime, 4)

    print('PROCESSED ' + str(MSG_COUNT) + ' RECORDS IN ' + str(avgTime) + ' SECONDS')

if __name__ == '__main__':
    execute(sys.argv[1])
