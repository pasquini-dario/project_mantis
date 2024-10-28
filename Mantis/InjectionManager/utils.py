import pickle, os

def make_text_invisible_terminal(text):
    return "\033[8m %s \033[0m" % text
    
def mkdir(path):
    try:
        os.mkdir(path)
    except FileExistsError:
        ...

def read_pickle(path):
    with open(path, 'rb') as f:
        data = pickle.load(f)
    return data

def write_pickle(path, data):
    with open(path, 'wb') as f:
        data = pickle.dump(data, f)
        
def make_text_invisible_terminal(text):
    return "\033[8m %s \033[0m" % text    

def html_comment(text):
    return f'<!-- {text} -->'

def append_payload(msg, keyword, payload, invisible_shell=True, invisible_html=False):
    if invisible_shell:
       payload = make_text_invisible_terminal(payload)
    if invisible_html:
        payload = html_comment(payload)
    return msg.rstrip()  + payload
