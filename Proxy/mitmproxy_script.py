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
	__lastConnectionAddress = ("",0)

	@staticmethod
	def reset():
		RedirectionChain.objects().delete()
		Url.objects(parser="mitmproxy_script").delete()

	def set_static_redirection_chain(self, url, connectionAddrs):
		if len(MitmScript.__staticInitUrl) == 0:
			MitmScript.reset()
			MitmScript.__setStaticInitUrl(url)
			urlObj = self.save_url_to_db(url)
			redirectionChain = RedirectionChain(init_url = url, count = 0)
			redirectionChain.chain.append(urlObj)
			redirectionChain.count += 1
			redirectionChain.save()

		if MitmScript.__lastConnectionAddress == ("",0):
			MitmScript.__set_lastConnectionaddress(connectionAddrs)

	@staticmethod
	def __setStaticInitUrl(url):
		MitmScript.__staticInitUrl = url

	@staticmethod
	def __set_lastConnectionaddress(*address):
		MitmScript.__lastConnectionAddress = address[0]

	def request(self, flow):
		if flow.server_conn.address:
			connectionAddrs = flow.server_conn.address.address
		elif flow.request:
			connectionAddrs = (flow.request.host, flow.request.port)

		if flow.request.method == "GET":
			curr_requested_url = flow.request.url
			redirection_candidates = self.load_urls_from_db()
			self.set_static_redirection_chain(curr_requested_url, connectionAddrs)
			for candidate in redirection_candidates:
				if curr_requested_url == candidate and curr_requested_url != self.__staticInitUrl:
					logger.debug("[MitmScript] candidate match! " + curr_requested_url + " == " + candidate)
					urlObj = self.save_url_to_db(candidate)
					redirection_chain = RedirectionChain.objects(init_url = MitmScript.__staticInitUrl).first()
					self.add_url_to_chain(urlObj, redirection_chain)
					MitmScript.__set_lastConnectionaddress(connectionAddrs)

	def __last_url_in_chain(self, redirection_chain):
		last = redirection_chain.chain[len(redirection_chain.chain)-1].raw_data
		return last

	def response(self, flow):
		redirection = False
		redirection_candidates = []
		redirection_chain = RedirectionChain.objects(init_url=MitmScript.__staticInitUrl).first()
		if redirection_chain is None:
			return
		curr_connection_addr = flow.server_conn.address.address
		if curr_connection_addr == self.__lastConnectionAddress:
			# case: HTTP Redirects
			if flow.response.status_code in [301, 302, 307]:
				redirection = True
				redirectUrl = flow.response.headers.get("Location", )
				redirection_candidates.append(redirectUrl)
				logger.debug("[MitmScript] HTTP redirect candidate: " + redirectUrl)

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
							logger.debug("[MitmScript]HTML meta tag redirect candidate: " + redirectUrl)

			js_red = ['location']
			for red_code in js_red:
				urlBeg = urlEnd = -1
				loc = flow.response.content.find(red_code)
				if loc != -1:
					if flow.response.content.find('\"',loc) < flow.response.content.find('\'',loc) and flow.response.content.find('\"',loc) != -1:
						urlBeg = flow.response.content.find('\"',loc)
						urlEnd = flow.response.content.find('\"',urlBeg+1)
					elif flow.response.content.find('\'',loc) != -1:
						urlBeg = flow.response.content.find('\'', loc)
						urlEnd = flow.response.content.find('\'', urlBeg + 1)

					if urlBeg+1 < urlEnd and urlBeg != -1:
						redirectUrl = flow.response.content[urlBeg+1:urlEnd]
						redirection_candidates.append(redirectUrl)
						logger.debug("[MitmScript] Javascript redirect candidate: " + redirectUrl)

			self.save_urls_to_db(redirection_candidates)

	@staticmethod
	def script_path():
		path = os.path.abspath(__file__)
		return path

	def add_url_to_chain(self, urlObj, RedChainObj):
		RedChainObj.chain.append(urlObj)
		RedChainObj.count += 1
		RedChainObj.save()

	def save_urls_to_db(self, urls):
			for url in urls:
				self.save_url_to_db(url)

	def load_urls_from_db(self):
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

	def save_url_to_db(self, raw_url):
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
