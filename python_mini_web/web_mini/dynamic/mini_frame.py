
import re
from pymysql import connect

# 定义一个字典，以键值对的形式存储{ '/index.py':index}
URL_FUNC_DICT = dict()

# 定义一个闭包，但是装饰一要传入字典的键名，所以在最外层定义一个函数route
def route(url_content):
    def set_func(func):
        URL_FUNC_DICT[url_content] = func  # 以键值对的形式存储到字典中
        def call_func(*args,**kwargs):
            return func(*args,**kwargs)
        return call_func
    return set_func


# 先将参数传入，获取到route函数的返回值，再用其进行装饰   等价于  url_content = '/index.py' 
# index = set_func(index)  注意：此时内层函数set_func因为闭包可以访问url_content
@route('/index.html')  
def index():
    # open中的文件的路径是参考web0server.py文件
    with open('./templates/index.html') as fr:
        content = fr.read()

    # 模板
    tr_template = """<tr>
        <td>%s</td>
        <td>%s</td>
        <td>%s</td>
        <td>%s</td>
        <td>%s</td>
        <td>%s</td>
        <td>%s</td>
        <td>%s</td>
        <td>
            <input type="button" value="添加" id="toAdd" name="toAdd" systemidvaule="000007" />
        </td>
        </tr>
    """

    # 创建Connection连接
    conn = connect(host='localhost',port=3306,database='stock_db',user='root',password='123456',charset='utf8')
    # 获得Cursor对象
    cs = conn.cursor()
    # python解释器执行sql语句 同时将查询结果存储在cs中
    cs.execute('select * from info;')
    # 获取cs中全部的查询结果
    stock_info = cs.fetchall()
    # 关闭游标，链接
    cs.close()
    conn.close()

    # 将模板和数据库数据进行组合
    html = ""
    for line_info in stock_info:
        html += tr_template % (line_info[0],line_info[1],line_info[2],line_info[3],line_info[4],line_info[5],line_info[6],line_info[7])

    # 使用正则替换掉制定的字符串   实际上是修改完页面的源代码和数据库的数据同时，返回给body
    content = re.sub(r"\{%content%\}",html,content)

    return content

@route('/center.html')
def center():
    with open('./templates/center.html') as fr:
        content = fr.read()

    # 创建Connection连接
    conn = connect(host='localhost',port=3306,database='stock_db',user='root',password='123456',charset='utf8')
    # 获得Cursor对象
    cs = conn.cursor()
    # python解释器执行sql语句 同时将查询结果存储在cs中
    cs.execute('select i.code,i.short,i.chg,i.turnover,i.price,i.highs,f.note_info from info as i inner join focus as f on f.id = i.id;')
    # 获取cs中全部的查询结果
    stock_info = cs.fetchall()
    cs.close()
    conn.close()
    tr_template = """
        <tr>
            <td>%s</td>
            <td>%s</td>
            <td>%s</td>
            <td>%s</td>
            <td>%s</td>
            <td>%s</td>
            <td>%s</td>
            <td>
                <a type="button" class="btn btn-default btn-xs" href="/update/300268.html"> <span class="glyphicon glyphicon-star" aria-hidden="true"></span> 修改 </a>
            </td>
            <td>
                <input type="button" value="删除" id="toDel" name="toDel" systemidvaule="300268">
            </td>
        </tr>
    """

    html = ""
    for line_info in stock_info:
        html += tr_template % (line_info[0],line_info[1],line_info[2],line_info[3],line_info[4],line_info[5],line_info[6])

    # 使用正则替换掉制定的字符串
    content = re.sub(r"\{%content%\}",html,content)
    return content


@route('/indexs.html')
def indexs():
    with open('./templates/indexs.html') as fr:
        content = fr.read()
    return content

"""
# 定义字典，根据关键字，存储对应函数的引用
URL_FUNC_DICT = {
    "/index.py":index,
    "/center.py":center,
    "/indexs.py":indexs
}
"""

def application(environ, start_response):
    # 因为这是WSGI规定好的函数，相当于给函数传递两个参数
    start_response('200 OK', [('Content-Type', 'text/html;charset=utf-8')])  # 注意：服务器的相关信息不应该在此处添加
    file_name = environ['PATH_INFO']  # file_name获取到的是url中输入的参数 如:index.py
    try:
        func = URL_FUNC_DICT[file_name]  # func 实际上就是函数的引用  如： index  indexs  center
        return func()  # 实现装饰器的调用    
    except Exception as ret:
        return '产生异常....%s'%str(ret)

    """
    if file_name == '/index.py':
        return index()

    elif file_name == '/center.py':
        return center()

    elif file_name == '/indexs.py':
        return indexs()

    else:
        return '你好 World!'
    """

