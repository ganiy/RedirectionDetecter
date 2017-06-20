import multiprocessing

from mitmproxy.main import mitmdump

from Model.webdriver import Browser

if __name__ == '__main__':
    initial_url = "http://10.0.75.1/redirect2.html"
    #initial_url = "http://google.com"

#change to subprocess
    p = multiprocessing.Process(target=mitmdump, args=("-s 'C:\Users\ganiy\PycharmProjects\RedirectionDetecter\Proxy\mitmproxy_script.py'",))
    p.start()


    browser = Browser()
    title = browser.get_url(initial_url)
    print title
    browser.quit()

    if p.is_alive():
        p.terminate()


