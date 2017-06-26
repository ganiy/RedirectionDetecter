import multiprocessing
import time

import logging
from mitmproxy.main import mitmdump
from Model.webdriver import Browser
from Proxy.mitmproxy_script import MitmScript
from orm import RedirectionChain

logger = logging.getLogger('root')

class RedirectionDetecter(object):

    def __init__(self):
        try:
            super(self.__class__, self).__init__()
            MitmScriptPath = MitmScript.script_path()
            if MitmScriptPath[len(MitmScriptPath)-1].lower() == 'c':
                MitmScriptPath = MitmScriptPath[:len(MitmScriptPath)-1]
            # MitmScriptPath1 = "C:\Users\ganiy\PycharmProjects\RedirectionDetecter\Proxy\mitmproxy_script.py"
            self.mitm_process = multiprocessing.Process(target=mitmdump, args=("-s " + MitmScriptPath,))
            self.mitm_process.start()
            logger.debug("RedirectionDetecter: Mitmdump process initiated")
        except Exception,e:
            logger.error(e.message)

    def find_redirection_chain(self, url):
        try:
            self.__initURL = url
            if self.mitm_process.is_alive() == False:
                self.__init__()
            browser = Browser()
            browser.get_url(url)
            browser.quit()
            self.kill()
            return self.__get_chain()
        except Exception,e:
            logger.error(e.message)

    def __get_chain(self):
        try:
            time.sleep(5)
            urls = []
            redirection_chain = RedirectionChain.objects.first()
            if redirection_chain:
                for urlObj in redirection_chain.chain:
                    urls.append(urlObj.raw_data)
            return urls
        except Exception,e:
            logger.error(e.message)

    def kill(self):
        try:
            if self.mitm_process.is_alive():
                logger.debug("RedirectionDetecter: mitmdump process terminated")
                self.mitm_process.terminate()
        except Exception,e:
            logger.error(e.message)