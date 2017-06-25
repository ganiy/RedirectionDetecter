import traceback
from Model.RedirectionDetecter import RedirectionDetecter


if __name__ == '__main__':
    try:
        initial_url = "http://w3schools.com"
        rd = RedirectionDetecter()
        print rd.find_redirection_chain(initial_url)

        initial_url = "http://10.0.75.1/redirect1.html"
        print rd.find_redirection_chain(initial_url)

    except Exception, e:
        print e.message
        print traceback.format_exc()







