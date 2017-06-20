from Model.RedirectionDetecter import RedirectionDetecter

if __name__ == '__main__':
    #initial_url = "http://10.0.75.1/redirect1.html"
    initial_url = "http://google.com"
try:
    rd = RedirectionDetecter()
    rd.find_redirection_chain(initial_url)
    rd.kill()
except Exception, e:
    pass







