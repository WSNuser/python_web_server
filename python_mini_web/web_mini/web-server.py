
import re
import socket
import multiprocessing
# import dynamic.mini_frame
import sys

class WSGIServer(object):

	def __init__(self,port,app,static_path):
		
		# 1-创建套接字
		self.tcp_server_socket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
		
		# 设置套接字选项  避免先终止服务器因保留的资源时间而导致再次开启时出现问题
		self.tcp_server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

		# 2-绑定本地信息
		self.tcp_server_socket.bind(("",port))

		# 3-设置被动
		self.tcp_server_socket.listen(128)

		self.app = app

		self.static_path = static_path

	# 通过在框架中被调用，同时对传入的两个参数进行存储
	# 该函数的目的：将框架返回的数据和服务器的信息合并
	def set_response_header(self,status,headers): # headers = [('Content-Type', 'text/html')]  即框架中的信息
		self.status = status   #‘200 ok’
		self.headers = [('serevr','mini-web 1.0')]    # 服务器自己的信息

		self.headers +=headers
	# 通过创建一个tcp的服务器模拟web服务器相应浏览器

	def server_func(self,new_socket):
		
		# 接收客户端发送的请求
		recv_requests = new_socket.recv(1024).decode("utf-8")

		# 打印客户端发送的请求
		print(recv_requests)	
		
		# GET /index.html HTTP/1.1 
		response_content = recv_requests.splitlines()[0]  # 将浏览器发送的请求信息进行按行分割并存入列表中，同时取出列表中的第一个字符串
		
		# 通过正则表达式将需要访问网页的html提取出来
		html_str = re.search(r".*?\s(.*?)\s.*",response_content).group(1)

		# 设置网站打开的默认页
		if html_str == "/":
			html_str += "index.html"
		# print(html_str)
		# print(type(html_str))

		# 如果不是以py结尾，加载页面时图片，css等文件的获取
		if not html_str.endswith('.html'):
			try:  # 当读取文件的时候出现异常，跳转到except中


				# 因为当发现html文件中需要访问其他资源的时候(如css,js)，则重新发送请求
				# 同时open中的路径也是要参考当前文件的路径
				f = open(self.static_path+html_str,"rb")
				html_content = f.read()	

			except:  # 页面异常的设置

				response = "HTTP/1.1 404 NOT FOUND!\r\n"
		 
				response += "\r\n"
			
				response += "抱歉，当前页面没有找到...."

				new_socket.send(response.encode("gbk"))

			else:  # 读取文件没有出现异常

				# 响应浏览器
				response = "HTTP/1.1 200 OK\r\n"  # \r\n可以理解为回车  响应头
				
				response += "\r\n"  # 响应头和内容要用一个空行隔开

				new_socket.send(response.encode("utf-8"))  # 发送响应头给浏览器

				new_socket.send(html_content)  # 发送响应体给浏览器，因为之前以rb形式读取，所以不用进行编码

			# 关闭套接字
			new_socket.close()
		else:
			# 动态资源的请求
			
			# body = mini_frame.login()
			# 定义一个空字典
			env = dict()
			env['PATH_INFO'] = html_str
			# 跳转到框架中的函数，同时传递两个参数   参数1——字典类型   参数2——函数的引用
			body = self.app(env,self.set_response_header)
			
			header = "HTTP/1.1 %s\r\n"%(self.status) #补全响应头中
			for x in self.headers: # x为列表中的元组
				header += "%s:%s\r\n"%(x[0],x[1])
			header += "\r\n" # 空行

			response = header + body
			new_socket.send(response.encode("utf-8"))  # 发送响应头给浏览器

	def run_forever(self):
		

		while True:

			# 4-等待服务器链接 	
			new_socket,address = self.tcp_server_socket.accept()

			# 5-服务器接收请求后的相应操作 
			p = multiprocessing.Process(target = self.server_func, args = (new_socket,))

			p.start()

			# ***注意：创建一个进程相当于当前的资源重新创建一份，可以理解为当前的文件的硬链接数是2，所以不仅要在子进程中关闭当前浏览器套接字，还要在主进程中关闭套接字
			new_socket.close()

		# 关闭监听套接字
		self.tcp_server_socket.close()

def main():
	if len(sys.argv) == 3:
		try:
			port = int(sys.argv[1])
		except Exception as ret:
			print('端口号输入错误....')
			return

		# 
		with open('./web-server.conf') as f:
			conf_info = eval(f.read())  # 将字符串转换为字典,注意不能使用dict()的方式，eval往往用于将字典格式的字符串转换为字典

		# 添加模块系统目录  从字典中获取值
		sys.path.append(conf_info['dynamic_path'])
		
		frame_temp_name = sys.argv[2]  # mini_frame:application
		#print(frame_temp_name)
		frame_name_str = re.match(r"([^:]+):(.*)",frame_temp_name)
		frame_name = frame_name_str.group(1)  # mini_frame
		app_name = frame_name_str.group(2)  # application

		# import frame_name  实际上去找frame_name.py这个文件

		frame = __import__(frame_name)  # 返回值返回这个导入的模块
		app = getattr(frame,app_name)  #将模块和函数相关联，即当调用app函数时，默认就会调用frame模块下面的app_name这个函数 

	wsgi_server = WSGIServer(port,app,conf_info['static_path'])
	wsgi_server.run_forever()



if __name__ == "__main__":
	main()


'''
总结：当tcp服务器和浏览器相关联时，发送与接收的数据并不像我们之前那样简单，
	涉及到相应的HTTP协议，涉及到请求头，响应头，响应体,注意响应头和响应体之间要用空行隔开,
	

'''


