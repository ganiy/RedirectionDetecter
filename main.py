import logging

from Model.RedirectionDetecter import RedirectionDetecter

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s %(levelname)s [%(pathname)s:%(lineno)s] %(message)s',
                    filename='/var/log/phishXposed.log',
                    filemode='a')

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger('root')

if __name__ == '__main__':
    initial_url = "http://walla.co.il"
    rd = RedirectionDetecter()
    print rd.find_redirection_chain(initial_url)








