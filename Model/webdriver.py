from selenium import webdriver
from selenium.webdriver import DesiredCapabilities

PROXY = "127.0.0.1:8080"

service_args = [
    '--ignore-ssl-errors=true',
    '--web-security=no',
    '--ssl-protocol=any',
    '--proxy=127.0.0.1:8080',
    '--proxy-type=https']

phantomjs_path = "/usr/bin/phantomjs"

capabilities = DesiredCapabilities.PHANTOMJS
# capabilities["phantomjs.page.settings.javascriptEnabled"] = "false"

class Browser():

    driver = None

    def __init__(self):
        self.driver = webdriver.PhantomJS(service_args=service_args, desired_capabilities= capabilities,
                                         executable_path=phantomjs_path, service_log_path="/var/log/phantomjs.log")
        self.driver.set_page_load_timeout(60)
        print "Browser: PhantomJS webdriver initiated"


    def get_url(self, url):
        print "Browser: GET " + url
        self.driver.get(url)
        location = self.driver.execute_script('return document.URL;')
        return self.driver.title + " " + location

    def quit(self):
        self.driver.quit()
        print "Browser: webdriver exited"
