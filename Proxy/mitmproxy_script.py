import hashlib
import os
import traceback
from urlparse import urlparse

import logging
from bs4 import BeautifulSoup

from orm import Url, RedirectionChain

logger = logging.getLogger('root')


class MitmScript:
	__staticInitUrl = ""

	@staticmethod
	def set_static_redirection_chain(url):
		if len(MitmScript.__staticInitUrl) == 0:
			MitmScript.delete_redirection_chains()
			MitmScript.__setStaticInitUrl(url)
			redirectionChain = RedirectionChain(init_url = url, count = 0)
			redirectionChain.save()

	@staticmethod
	def delete_redirection_chains():
		Url.objects(parser="mitmproxy_script").delete()
		RedirectionChain.objects().delete()

	@staticmethod
	def __setStaticInitUrl(url):
		MitmScript.__staticInitUrl = url

	def request(self, flow):
		# print("[request] " + flow.request.method + " " + flow.request.url)
		# print("[request header] " + str(flow.request.headers))
		if flow.request.method == "GET":
			redirection_candidates = load_urls_from_db()
			MitmScript.set_static_redirection_chain(flow.request.url)
			for candidate in redirection_candidates:
				if flow.request.url == candidate:
					print("match! " + flow.request.url + " == " + candidate)
					urlObj = save_url_to_db(candidate)
					redirection_chain = RedirectionChain.objects(init_url = MitmScript.__staticInitUrl).first()
					redirection_chain.chain.append(urlObj)
					redirection_chain.count += 1
					redirection_chain.save()
				else:
					print("no match: " + flow.request.url + " != " + candidate)

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

		js_red = ['window.location','top.location','application.location']
		for red_code in js_red:
			urlBeg = urlEnd = -1
			loc = flow.response.content.find(red_code)
			if loc != -1:
				#TODO should add support for (')
				if flow.response.content.find('\"',loc) < flow.response.content.find('\'',loc) and flow.response.content.find('\"',loc) != -1:
					urlBeg = flow.response.content.find('\"',loc)
					urlEnd = flow.response.content.find('\"',urlBeg+1)
				elif flow.response.content.find('\'',loc) != -1:
					urlBeg = flow.response.content.find('\'', loc)
					urlEnd = flow.response.content.find('\'', urlBeg + 1)

				if urlBeg+1 < urlEnd and urlBeg != -1:
					redirectUrl = flow.response.content[urlBeg+1:urlEnd]
					redirection_candidates.append(redirectUrl)
					print("[Javascript Redirect] redirect to: " + redirectUrl)

		save_urls_to_db(redirection_candidates)
		# print(redirection_candidates)

		# print(flow.response.content)

	@staticmethod
	def script_path():
		path = os.path.abspath(__file__)
		return path

def save_urls_to_db(urls):
		for url in urls:
			save_url_to_db(url)

def load_urls_from_db():
	urls = []
	try:
		urlObjs = Url.objects(parser="mitmproxy_script")
		for urlObj in urlObjs:
			urls.append(urlObj.raw_data)
		return urls
	except Exception, e:
		logger.error(e.message)
		logger.error(traceback.format_exc())
		return []

def save_url_to_db(raw_url):
	try:
		o = urlparse(raw_url)
		fhash = hashlib.sha256()
		fhash.update(raw_url)
		urlObj, created = Url.objects.get_or_create(sha256=fhash.hexdigest(), raw_data=o.geturl(),
													domain=o.netloc, protocol=o.scheme, path=o.path,
													query=o.query, port=str(o.port), parser="mitmproxy_script")
		urlObj.save()
		return urlObj
	except Exception, e:
		logger.error(e.message)
		logger.error(traceback.format_exc())
		return None

def start():
	return MitmScript()