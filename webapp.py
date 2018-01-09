#!/usr/bin/python
# -*- conding:utf-8 -*-
from bottle import route, run, static_file
@route('/')
def hello():
    return ("/index.html")
test_home = './resource/'
@route('/<p:path>')
def foo(p):
    return static_file(p, test_home)
run(host='localhost', port=8080)