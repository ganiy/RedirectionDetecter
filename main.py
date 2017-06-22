import traceback
import logging
from Model.RedirectionDetecter import RedirectionDetecter

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s %(levelname)s [%(pathname)s:%(lineno)s] %(message)s',
                    filename='/var/log/phishXposed.log',
                    filemode='a')
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger('root')

if __name__ == '__main__':
    # initial_url = "http://10.0.75.1/redirect1.html"
    initial_url = "https://walla.co.il"
    try:
        rd = RedirectionDetecter()
        print rd.find_redirection_chain(initial_url)
        rd.kill()
    except Exception, e:
        print e.message
        print traceback.format_exc()







