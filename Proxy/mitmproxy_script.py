from bs4 import BeautifulSoup


class PrintRequest:
	def request(self, flow):
		pass
		# print("[request] " + flow.request.method + " " + flow.request.url)
		# print("[request header] " + str(flow.request.headers))

	def response(self, flow):
		redirection = False

		# case: HTTP Redirects
		if flow.response.status_code in [301, 302, 307]:
			redirection = True
			print("[HTTP Redirects] redirect to: " + flow.response.headers.get("Location", ))

		# case: <meta http-equiv="Refresh" content="0; url=http://www.example.com/" />
		if flow.response.headers.get("Content-Type",).startswith("text/html"):
			redirectUrl = ''
			html = BeautifulSoup(flow.response.content, "html.parser")
			metaTags = html.find_all(name='meta', attrs={'http-equiv': 'Refresh'})
			for metaTag in metaTags:
				if metaTag.has_attr('content'):
					content = metaTag['content'].split('url=')
					if len(content)>1:
						redirection = True
						redirectUrl = content[1]
						print("[HTML Meta refresh] redirect to: " + redirectUrl)




		if flow.response.headers.get("Content-Type",) is "text/html" :
			print("[response]" +flow.response.content)



def start():
	return PrintRequest()