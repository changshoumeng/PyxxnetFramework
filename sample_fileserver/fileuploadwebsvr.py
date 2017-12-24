#!/usr/bin/env python
# -*- coding: utf-8 -*-

import BaseHTTPServer, SocketServer, cgi
from os import curdir, sep, path
import time
import random
import urllib
import urllib2


uploadhtml = '''<html><body>
<p>批量文件上传</p>
<form enctype="multipart/form-data" action="/" method="post">
<p>File: <input type="file" name="file1"></p>
<p><input type="submit" value="上传"></p>
</form>
</body></html>'''





def doPost(url,content):
    urllib2.socket.setdefaulttimeout(5)
    request = urllib2.Request(url, content)
    request.add_header('User-Agent', 'Mozilla/5.0 (Windows NT 5.1; rv:14.0) Gecko/20100101 Firefox/14.0.1')
    request.add_header('Content-Type', 'application/x-www-form-urlencoded')
    try:
        response = urllib2.urlopen(request)
        page = response.read()
        return page
    except Exception,e:
        t= "caught a exption:{0}".format(e.message)
        return t
    return "error"


def verifyImage(fileName):
    if not  path.exists(fileName):
        print "not exist filename:{0}".format(fileName)
        return None
    with open(fileName,'rb') as f:
        data=f.read()
        return doPost("http://127.0.0.1:8081",data)





class WebHandler(BaseHTTPServer.BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/':
            self.send_response(200)
            self.send_header('Content-Type', 'text/html; charset=utf-8')
            self.end_headers()
            self.wfile.write(uploadhtml)
            return
        try:
            f = open(curdir + sep + self.path)
            self.send_response(200)
            self.end_headers()
            self.wfile.write(f.read())
            f.close()
        except IOError:
            self.send_error(404, 'File Not Found: %s' % self.path)

    def do_POST(self):
        form = cgi.FieldStorage(fp=self.rfile,
                                headers=self.headers,
                                environ={'REQUEST_METHOD': 'POST', 'CONTENT_TYPE': self.headers['Content-Type'], })
        self.send_response(200)
        self.send_header('Content-Type', 'text/html; charset=utf-8')
        self.end_headers()
        self.wfile.write('<Html>上传完毕。<br/><br/>');
        self.wfile.write('客户端: %s<br/>' % str(self.client_address))
        for field in form.keys():
            field_item = form[field]
            if field_item.filename:
                strfilename = field_item.filename
                strfilename=strfilename.lower()
                if strfilename.find("jpg")<0 and  strfilename.find("jpeg")<0:
                    self.wfile.write("请上传jpg图片，仅支持此种类型图片")
                else:
                    tm_lable=time.strftime("%Y%m%d%H%M%S", time.localtime(time.time()))
                    strfilename = tm_lable+str(random.randint(0,100000))+strfilename
                    fn = curdir + sep + "data"+sep+strfilename
                    print fn
                    upfile = open(fn, 'w')
                    file_data = field_item.file.read()
                    upfile.write(file_data)
                    upfile.close()
                    file_len = len(file_data)
                    del file_data
                    self.wfile.write('文件 <a href="%s">%s</a> 成功上传，尺寸为：%d bytes<br/>' % (
                    field_item.filename, field_item.filename, file_len))
                    result = verifyImage(fn)
                    if result:
                        self.wfile.write('<p>'+result+'</p>')
                    else:
                        result="Error"
                        self.wfile.write('<p>' + result + '</p>')

        self.wfile.write('</html>')

path.exists()

class ThreadingHTTPServer(SocketServer.ThreadingMixIn, BaseHTTPServer.HTTPServer):
    pass


if __name__ == '__main__':
    server_address = ('0.0.0.0', 8480)
    httpd = ThreadingHTTPServer(server_address, WebHandler)
    print "Web Server On %s:%d" % server_address
    httpd.serve_forever()
