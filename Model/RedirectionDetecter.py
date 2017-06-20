import multiprocessing
from mitmproxy.main import mitmdump
from Model.webdriver import Browser
from Proxy.mitmproxy_script import MitmScript



class RedirectionDetecter(object):

    def __init__(self):
        super(self.__class__, self).__init__()
        # MitmScriptPath = MitmScript.script_path()
        MitmScriptPath = "C:\Users\ganiy\PycharmProjects\RedirectionDetecter\Proxy\mitmproxy_script.py"
        self.mitm_process = multiprocessing.Process(target=mitmdump, args=("-s " + MitmScriptPath,))
        self.mitm_process.start()

    def find_redirection_chain(self, url):
        if self.mitm_process.is_alive():
            browser = Browser()
            title = browser.get_url(url)
            print title
            browser.quit()
        else:
            print 'RedirectionDetecter Exception: mitmdump is not running'
            raise Exception('RedirectionDetecter: mitmdump is not running')

    def kill(self):
        if self.mitm_process.is_alive():
            print "RedirectionDetecter: mitmdump process terminated"
            self.mitm_process.terminate()