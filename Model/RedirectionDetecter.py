import multiprocessing
import time

from mitmproxy.main import mitmdump
from Model.webdriver import Browser
from Proxy.mitmproxy_script import MitmScript
from orm import RedirectionChain


class RedirectionDetecter(object):

    def __init__(self):
        super(self.__class__, self).__init__()
        # MitmScriptPath = MitmScript.script_path()
        MitmScriptPath = "C:\Users\ganiy\PycharmProjects\RedirectionDetecter\Proxy\mitmproxy_script.py"
        self.mitm_process = multiprocessing.Process(target=mitmdump, args=("-s " + MitmScriptPath,))
        self.mitm_process.start()

    def find_redirection_chain(self, url):
        self.__initURL = url
        if self.mitm_process.is_alive() == False:
            self.__init__()
        browser = Browser()
        browser.get_url(url)
        browser.quit()
        self.kill()
        return self.__get_chain()

    def __get_chain(self):
        time.sleep(5)
        urls = []
        redirection_chain = RedirectionChain.objects.first()
        if redirection_chain:
            for urlObj in redirection_chain.chain:
                urls.append(urlObj.raw_data)
        return urls


    def kill(self):
        if self.mitm_process.is_alive():
            print "RedirectionDetecter: mitmdump process terminated"
            self.mitm_process.terminate()