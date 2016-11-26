#!/bin/env python3
# -*- coding:utf-8 -*-
import re
import sys
import gzip,tarfile
import zipfile
import os,time,datetime
import os.path
import mysql.connector
import urllib.parse

oneday = datetime.timedelta(days=1)
today_time = datetime.datetime.now()
yesterday_time = datetime.datetime.now() - oneday
yesterday_time=datetime.datetime.strftime(yesterday_time, '%Y%m%d')

logP=r"^\"-\"|/(static)|/(nocache)|/(block)|(.css)|(.js)|(.jpg)|/(v6)|/(getWelcomeImages)|/(robots.txt)|/(favicon.ico)|(helper/)|(spider)|(bingbot/2.0)|(/zhifu/WxpayStatus)|(/api)|(/rest)|/robots.txt"
logarr=r"^\"-\"|/static|/nocache|/block|\\.css|\\.js|\\.jpg|/v6|/getWelcomeImages|/robots.txt|/favicon.ico|helper/|spider|/zhifu/WxpayStatus"
logPage=r"^/(static|(nocache)|(block))|(/api)|(/rest)|(/nproduct/randcustomer)|(/zhifu/WxpayStatus)"
# ipP = r"""?P<ip>[\d.]+"""
ipP = r"[\d.]+"
logPv=r"(\\x.?)|(\x00.?)"
logUv=r"(MIDP)|(WAP)|(UP.Browser)|(Smartphone)|(Obigo)|(Mobile)|(AU.Browser)|(wxd.Mms)|(WxdB.Browser)|(CLDC)|(UP.Link)|(KM.Browser)|(UCWEB)|(SEMC-Browser)|(Mini)|(Symbian)|(Palm)|(Nokia)|(Panasonic)|(MOT-)|(SonyEricsson)|(NEC-)|(Alcatel)|(Ericsson)|(BENQ)|(BenQ)|(Amoisonic)|(Amoi-)|(Capitel)|(PHILIPS)|(SAMSUNG)|(Lenovo)|(Mitsu)|(Motorola)|(SHARP)|(WAPPER)|(LG-)|(LG/)|(EG900)|(CECT)|(Compal)|(kejian)|(Bird)|(BIRD)|(G900/V1.0)|(Arima)|(CTL)|(TDG)|(Daxian)|(DAXIAN)|(DBTEL)|(Eastcom)|(EASTCOM)|(PANTECH)|(Dopod)|(Haier)|(HAIER)|(KONKA)|(KEJIAN)|(LENOVO)|(Soutec)|(SOUTEC)|(SAGEM)|(SEC-)|(SED-)|(EMOL-)|(INNO55)|(ZTE)|(iPhone)|(Android)|(Windows CE)|(Wget)|(Java)|(curl)|(Opera)"
log=r"(www.bxd365.com)|(m.bxd365.com)"
logua=r""

class PV(object):
    def __init__(self,line):
        self.line = line
    def print_page(self):
        line = self.line
        matchs =  re.search(logPv,line)
        if matchs !=None :
           pv=None
        else:
            try:
                if len(line.split("?")) > 1:
                    pv = line.split("?")[0]
                    pvage=line.split("?")[1]
                    pvage=str(pvage)
                else:
                    pv=line.split("?")[0]
                    pvage=None
            except TypeError as e:
               print('pv error! is {}'.format(e))
            pvage=pvage
        return pv,pvage;
class UV(object):
    def __init__(self,line):
        self.line = line
    def print_uv(self):
        line = self.line
        matchs = re.search(logUv,line)
        uv = line
        if matchs :
           uv_id=0
        else:
            uv_id=1

        return uv,uv_id;
class Log_items(object):
    log_items = ['times', 'size']

    def __init__(self, logitems):
        self.logitems = logitems = {}.fromkeys(self.log_items, 0)

    def increment(self, status_times_size, is_size):
        '''''该方法是用来给host_info中的各个值加1'''
        if status_times_size == 'times':
            self.logitems['times'] += 1
        elif is_size:
            self.logitems['size'] = self.logitems['size'] + status_times_size
        else:
            self.logitems[status_times_size] += 1
    def get_value(self, value):
        '''''该方法是取到各个主机信息中对应的值'''
        return self.logitems[value]
def split_eache_line(line):
    separator='\t'
    line_dict=''
    args = re.split("\"|\"", line)
    try:
        ipL = args[1].split(",")[0].strip()
        page = args[3].split()[1].strip()
        pv = PV(page).print_page()
        page=pv[0]
        page=str(page)
        pvage=pv[1]
        reqmethod = args[3].split()[0].strip()
        status = args[4].split()[0].strip()
        status = int(status)
        refer = args[len(args) - 4].split("?")[0].strip()
        usr = re.split('\(|\)|;', args[len(args) - 2])
        usr=str(usr)
        user = ''
        if len(usr) >=5 or len(page) > 255 or len(pvage) >255:
            pass
        if len(usr) >= 5:
            for i in range(1, 5):
                user = user + usr[i]
        else:
            for i in range(1, len(usr)):
                user = user + usr[i]
        if len(page) > 255:
            page = page[0:255]
        if pvage!=None and len(pvage) > 255:
            pvage = pvage[0:255]
        user = UV(user).print_uv()
        uv = user[0]
        uv_id = user[1]
        taketime = args[len(args) - 1].split("(|)")[0].split()[0].strip()
        # website = args[3].split(",")[1].strip()
        website='server-d'
        analy_time = re.split('\[|\]|\+', args[2])[1][-9:-1].strip()
        bytes = args[len(args) - 1].split()[1]
        line_dict = (ipL, status, uv, analy_time, website, taketime, reqmethod, page,pvage, uv_id)
    except ValueError as e:
        print('split_eache error! is{}'.format(e))
    except TypeError as e:
        print(usr,page,'\n',args)
        print('split_eache error! is{}'.format(e))
    # except IndexError as e:
        print('split_eache error! is{}'.format(e))
    split_dict = line_dict
    return split_dict
class fileAnalysis(object):
    def __init__(self):
        self.report_dict=report_dict
        self.anatime_dict=anatime_dict
        self.total_request_times, self.total_traffic=0,0
    def log_report(self,log_arg,bytes):
        if log_arg not in self.report_dict:
            log_arg_obj=Log_items(log_arg)
            self.report_dict[log_arg]=log_arg_obj
        else:
            log_arg_obj=self.report_dict[log_arg]
        log_arg_obj.increment('times',False)
        try:
            bytes_sent = int(bytes)
        except ValueError:
            bytes_sent = 0
        log_arg_obj.increment(bytes_sent, True)
        return self.report_dict
    def anatime_report(self,log_arg,bytes):
        if log_arg not in self.anatime_dict:
            log_arg_obj=Log_items(log_arg)
            self.anatime_dict[log_arg]=log_arg_obj
        else:
            log_arg_obj=self.anatime_dict[log_arg]
        log_arg_obj.increment('times',False)
        try:
            bytes_sent = int(bytes)
        except ValueError:
            bytes_sent = 0
        log_arg_obj.increment(bytes_sent, True)
        return self.anatime_dict
    def return_sorted_list(self,true_dict):
        for host_key in true_dict:
            host_value = true_dict[host_key]
            times = host_value.get_value('times')
            self.total_request_times = self.total_request_times + times
            size = host_value.get_value('size')
            self.total_traffic = self.total_traffic + size
            true_dict[host_key] = {'times': times, 'size': size}
        sorted_list = sorted(true_dict.items(), key=lambda t: (t[1]['times'], \
                                                                 t[1]['size']), reverse=True)
        return sorted_list

class Main(object):
    def main(self):
        conn = mysql.connector.connect(user='root', password='123456',host='192.168.1.23',port='3306', database='test',charset='utf8')
        global table
        # table='log_details_'+yesterday_time
        table='log_details_test'
        sql_delete_table='DROP TABLE IF EXISTS `%s`;' % table
        sql_create_table = 'CREATE TABLE `%s` (\
            `ld_id` int(11) NOT NULL AUTO_INCREMENT,\
            `ld_site` varchar(30) DEFAULT NULL,\
            `ld_ip` varchar(15) DEFAULT NULL,\
            `ld_time` time DEFAULT NULL,\
            `ld_method` varchar(10) DEFAULT NULL,\
            `ld_path` varchar(255) DEFAULT NULL,\
            `ld_query` text,\
            `ld_status` varchar(10) DEFAULT NULL,\
            `ld_latency` float(7,4) DEFAULT NULL,\
            `ld_ua` varchar(255) DEFAULT NULL,\
            `ld_ismobile` tinyint(1) DEFAULT NULL,\
            `ld_label` tinyint(1) DEFAULT NULL,\
            PRIMARY KEY (`ld_id`),\
            KEY `site` (`ld_site`),\
            KEY `ip` (`ld_ip`),\
            KEY `path` (`ld_path`),\
            KEY `time` (`ld_time`)) ENGINE=InnoDB DEFAULT CHARSET=utf8;'% table
        cursor = conn.cursor()
        try:
            cursor.execute(sql_delete_table)
            cursor.execute(sql_create_table)
            cursor.execute('set names utf8')
        except mysql.connector.Error as e:
            print('create table orange fails!{}'.format(e))
        infilename = os.path.split(sys.argv[1])[1]
        newlogname = infilename.split('-')[0] + '.txt'
        global newfile
        newfile = os.path.join('/root/prodcut/log/', newlogname)
        filezip = os.path.join('/data/www/log/',newlogname + '.zip')
        if os.path.exists(newfile):
            os.remove(newfile)
        arg_length = len(sys.argv)
        if arg_length == 1:
            print("Please Enter A Volid File !!")
        elif arg_length >= 2 :
            for i in range(1,arg_length):
                infile_name=sys.argv[i]
                try:
                    matchgz = re.search(r".*?gz$|.*?tar.gz$", infile_name)
                    matchzip = re.search(r".*zip$", infile_name)
                    if matchgz !=None:
                        infile = gzip.open(infile_name, 'rb')
                    elif matchzip !=None:
                        infile = zipfile.ZipFile(infile_name, 'rb')
                    else:
                        infile = open(infile_name, 'rb').readlines()
                except IOError:
                    print
                except ValueError:
                    print("Please Enter A Volid Number !!")
                global report_dict,anatime_dict
                report_dict={}
                anatime_dict={}
                sql_dict=[]
                i=0

                for line1 in infile:
                    line1 = line1.decode('utf8')
                    matchs = re.search(logP, line1)
                    if matchs != None:
                        continue
                    args = re.split("\"|\"", line1)
                    try:
                        ipL = args[1].split(",")[0].split(':')[0].strip()
                    except ValueError as e:
                        print('ipL error! is{}'.format(e))
                    except IndexError as e:
                        print('ipL error! is{}'.format(e))
                    matchs = re.search(ipP, ipL)
                    matchspv=re.search(logPv,line1)
                    if not line1 or len(line1.split()) == 0 or matchs == None or matchspv!=None:
                        # print(line1)
                        continue
                    split_dict=split_eache_line(line1)
                    sql_dict.append(split_dict)
                    # site=split_dict['site']
                    # bytes=split_dict['bytes_sent']
                    # status=split_dict['status']
                    # fileAnalysis_obj=fileAnalysis()
                    # report_dict=fileAnalysis_obj.log_report(site,bytes)
                    e = i % 500
                    if e == 0:
                        sql_insert = "insert into {0} (ld_ip,ld_status,ld_ua,ld_time,ld_site,ld_latency, ld_method,ld_path,ld_query,ld_ismobile) values\
                         (%s, %s,%s,%s,%s,%s,%s,%s,%s,%s)".format(table)
                        try:
                            # print(sql_dict)
                            # with open(newfile, 'a+') as f:
                            #     sql = "insert into %s (ld_site, ld_ip,ld_time,ld_method,ld_path,ld_status,ld_latency,ld_ua,ld_ismobile) values(%s);\n" % (
                            #     table, sql_dict)
                            #     f.write(sql)
                            cursor.executemany(sql_insert, sql_dict)
                            conn.commit()
                            sql_dict.clear()

                        except mysql.connector.Error as e:
                            print('insert datas error!{}'.format(e))
                            print(sql_insert % split_dict)
                    i=i+1




                    # report_dict=fileAnalysis_obj.log_report(status,bytes)
                    # print(report_dict)
                    # antime=split_dict['antime']
                    # seq=(antime,)
                    # anatime_dict=fileAnalysis_obj.anatime_report(seq,bytes)
                    # except  IOError:
                    #     print('there is some errors')
                # total_request_times,total_traffic=0,0
                # for host_key in report_dict:
                #      host_value = report_dict[host_key]
                #      times = host_value.get_value('times')
                #      total_request_times = total_request_times + times
                #      size = host_value.get_value('size')
                #      total_traffic = total_traffic + size
                #      report_dict[host_key]={'times':times,'size':size}
                # sorted_list = sorted(report_dict.items(), key=lambda t: (t[1]['times'], \
                #                                                         t[1]['size']), reverse=True)
                # print(sorted_list)
                # log_report = fileAnalysis_obj.return_sorted_list(anatime_dict)
                # print(log_report)
        conn.commit()
        cursor.close()
        conn.close()
        print ("Script Execution Time: %.3f second" % time.clock())
        # infile.close()

if __name__ == '__main__':
    main_obj = Main()
    main_obj.main()

