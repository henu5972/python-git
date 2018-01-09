import sys
import time
import re
import os
import json

ipP = r"?P<ip>[\d.]*"
ndP = r"?P<node>[\d]"
grP = r"?P<group>[A-Z]"
h = re.compile(r"(%s)" % (ipP), re.VERBOSE)
n = re.compile(r"(%s)" % (ndP), re.VERBOSE)
g = re.compile(r"(%s)" % (grP), re.VERBOSE)


class fileAnalysis(object):
    def __init__(self):
        '''''初始化一个空字典'''
        self.report_dict = {}
        # self.appname, self.host, self.group, self.node, self.http, self.https, self.ajp, self.shutdown, self.shutdown, self.jmx, self.dubbo
        self.a_list =['appname','host','group','node','http','https','ajp','shutdown','jmx','dubbo']
        self.a_dict={}.fromkeys(self.a_list, [])

    def split_eachline_todict(self, line):
        '''''分割文件中的每一行，并返回一个字典'''
        split_line = line.strip('\n').split('\t')
        split_dict = {'app': split_line[0], 'node': split_line[1], \
                      'group': split_line[2], 'ip': split_line[-1]}
        # print(split_dict)
        return split_dict
    def gen_port(self, app, node):
        # print(node)
        self.a_dict['http']= []
        self.a_dict['https']=[]
        self.a_dict['ajp']=[]
        self.a_dict['shutdown']=[]
        self.a_dict['jmx']=[]
        self.a_dict['dubbo']=[]
        if app.endswith('core'):
            num=30100
        elif app.endswith('control'):
            num=20100
        else:
            num=10100
        for i in range(1,node+1):
            self.a_dict['http'].append(num + 10 + i)
            self.a_dict['https'].append(num + 20 + i)
            self.a_dict['ajp'].append(num + 30 + i)
            self.a_dict['shutdown'].append(num + 40 + i)
            self.a_dict['jmx'].append(num + 50 + i)
            self.a_dict['dubbo'].append(num + 60+ i)
        return self.a_dict


    def generate_log_report(self, logfile):
        '''''读取文件，分析split_eachline_todict方法生成的字典'''
        total_list=[]
        for line in logfile:
            self.a_dict = {}.fromkeys(self.a_list, 0)
            try:
                if len(line) > 0:
                    line_dict = self.split_eachline_todict(line)
                    ip = line_dict['ip']
                    app = line_dict['app']
                    group = line_dict['group']
                    node = line_dict['node']
                    self.a_dict['appname']=app
                    self.a_dict['host'] = ip
                    self.a_dict['group'] = group
                    self.a_dict['node'] = node
                    matches = h.match(ip)
                    matches1 = n.match(node)
                    matches2 = g.match(group)
                    # print(ip,app,group,node)
                    if matches == None or matches1 == None or matches2 == None:
                        raise Exception
                    else:
                        if group != 'X':
                            port = self.gen_port(app,int(node))
                            # return port
                            # print(port)
                        else:
                            node = 1
                            port = self.gen_port(app, node)
                            # return port
                        # self.total_list.append((self.a_dict))
                        # print(self.a_dict)
                        # return self.a_dict
                        total_list.append((self.a_dict))
                    # return(total_list)

            except ValueError:
                continue
            except IndexError:
                continue
        return(total_list)


class zcmd(object):
    def main(self):
        '''''主调函数'''
        arg_length = 1
        if arg_length == 1:
            # infile_name = sys.argv[1]
            infile_name = 'G:/pytest/t.txt'
            try:
                with open(infile_name, 'r') as infile:
                    if arg_length == 3:
                        lines = int(sys.argv[2])
                    else:
                        lines = 0
                    fileAnalysis_obj = fileAnalysis()
                    not_true_dict = fileAnalysis_obj.generate_log_report(infile)
                    # fileAnalysis_obj.split_eachline_todict()
                    return (not_true_dict)
                    # for n in not_true_dict:
                    #      # return(json.dumps(n))
                    #       print(n)

            except ValueError:
                print
                print
                "Please Enter A Volid Number !!"


if __name__ == '__main__':
    maininfo = zcmd()
    maininfo.main()
