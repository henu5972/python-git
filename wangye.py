#coding:utf-8
from bottle import template,view
from creexcel import zcmd
import webbrowser
import json

#一些我们需要展示的文章题目和内容
articles = [("工程部署信息 ","详细信息链接","ex.html")]

excels= zcmd()
excel_items=excels.main()

@view('table_html')
def table(args):
    info={'args':args}
    return info
# print(excel_items)
# for i in excel_items:
    # print(i)
exhtml=table(excel_items)
# print(exhtml)
with open("resource/ex.html", 'wb') as f:
    f.write(exhtml.encode('utf-8'))
# print(excel_items)
html = template('template_html',items=articles)


with open("resource/index.html",'wb') as f:
    f.write(html.encode('utf-8'))


# 使用浏览器打开html
webbrowser.open("http://localhost:8080/index.html")