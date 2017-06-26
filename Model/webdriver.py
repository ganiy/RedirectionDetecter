import logging
from selenium import webdriver
from selenium.webdriver import DesiredCapabilities

logger = logging.getLogger('root')

class Browser():

    driver = None

    def __init__(self, proxy_ip_port = '127.0.0.1:8080'):
        service_args = [
            '--ignore-ssl-errors=true',
            '--web-security=no',
            '--ssl-protocol=any',
            '--proxy=' + proxy_ip_port,
            '--proxy-type=https']

        phantomjs_path = "/usr/bin/phantomjs"

        try:
            capabilities = DesiredCapabilities.PHANTOMJS

            self.driver = webdriver.PhantomJS(service_args=service_args, desired_capabilities= capabilities,
                                             executable_path=phantomjs_path, service_log_path="/var/log/phantomjs.log")
            self.driver.set_page_load_timeout(60)
            logger.debug("Browser: PhantomJS webdriver initiated")
        except Exception,e:
            logger.error(e.message)


    def get_url(self, url):
        try:
            logger.debug("Browser: GET " + url)
            self.driver.get(url)
            location = self.driver.execute_script('return document.URL;')
            return self.driver.title + " " + location
        except Exception,e:
            logger.error(e.message)

    def get_driver(self):
        return self.driver

    def quit(self):
        try:
            self.driver.quit()
            logger.debug("Browser: webdriver exited")
        except Exception,e:
            logger.error(e.message)
