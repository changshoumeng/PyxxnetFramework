import commands
import os
import time

def split_string(string_data='',sep=' '):
    str_arr0 = []
    str_arr1 = string_data.split(sep)
    for s in str_arr1:
        if not s:
            continue
        if s != sep:
            str_arr0.append(s)
    return  str_arr0


os.popen("").read()


def checkNetStat(port):
    print "--BEGIN"
    cmd = '''netstat -ant|egrep -i "{0}"|grep -v egrep'''.format(port)
    result = commands.getoutput(cmd)
    if not result:
        return "result is empty"
    line_list = result.split('\n')
    print "affect rows:",len(line_list)
    #tcp        1      0 10.10.2.220:34968       10.10.2.220:1234        CLOSE_WAIT
    #['tcp', '0', '0', '0.0.0.0:1234', '0.0.0.0:*', 'LISTEN']
    #0       1     2    3              4             5
    status_dict = {}
    for item in line_list:
        columns = split_string(item)
        status = columns[5]
        if status in status_dict:
            status_dict[status] += 1
        else:
            status_dict[status] = 1
    for k ,v in status_dict.items():
        print k,v
    print "--END"


def main():
    while True:
        checkNetStat("1234")
        time.sleep(1)

    pass


if __name__ == '__main__':
    main()
    pass
