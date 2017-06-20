import os

from bs4 import BeautifulSoup


class MitmScript:
	def request(self, flow):
		pass
		# print("[request] " + flow.request.method + " " + flow.request.url)
		# print("[request header] " + str(flow.request.headers))

	def response(self, flow):
		redirection = False
		redirection_candidates = []

		# case: HTTP Redirects
		if flow.response.status_code in [301, 302, 307]:
			redirection = True
			redirectUrl = flow.response.headers.get("Location", )
			redirection_candidates.append(redirectUrl)
			print("[HTTP Redirects] redirect to: " + redirectUrl)

		# case: <meta http-equiv="Refresh" content="0; url=http://www.example.com/" />
		content_type = flow.response.headers.get("Content-Type",)
		if content_type and content_type.startswith("text/html"):
			redirectUrl = ''
			html = BeautifulSoup(flow.response.content, "html.parser")
			metaTags = html.find_all(name='meta', attrs={'http-equiv': 'Refresh'})
			for metaTag in metaTags:
				if metaTag.has_attr('content'):
					content = metaTag['content'].lower().split('url=')
					if len(content)>1:
						redirection = True
						redirectUrl = content[1]
						redirection_candidates.append(redirectUrl)
						print("[HTML Meta refresh] redirect to: " + redirectUrl)

		js_red = ['location']
		for red_code in js_red:
			loc = flow.response.content.find(red_code)
			if loc != -1:
				#TODO should add support for (')
				urlBeg = flow.response.content.find('\"',loc)
				urlEnd = flow.response.content.find('\"',urlBeg+1)
				redirectUrl = flow.response.content[urlBeg+1:urlEnd]
				redirection_candidates.append(redirectUrl)
				print("[Javascript Redirect] redirect to: " + redirectUrl)

		print(redirection_candidates)

		print(flow.response.content)

	@staticmethod
	def script_path():
		path = os.path.abspath(__file__)
		return path


def start():
	return MitmScript()