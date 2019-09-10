from ftplib import FTP



ftp = FTP()
timeout = 30
port = 21
ftp.connect('104.241.203.194',21,timeout=10)
ftp.login('753databeyond','PqL159')
print (ftp.getwelcome())



def download_file():
    ftp.cwd('/')
    list = ftp.nlst()
    for name in list:
        print(name)
    
    return



def upload_file():
    return