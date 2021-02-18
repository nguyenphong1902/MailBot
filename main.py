import time
from mailbot import MailBot
from threading import Thread

# thread lấy email mới
def threaded_get_new_email(mb):
    print("thread running")
    while True:
        # mở inbox và tìm tất cả email có tag UNSEEN
        mb.con.select('INBOX')
        result, data = mb.con.search(None, 'UNSEEN')
        if result == 'OK'and len(data[0])>0:
            print("New email: "+str(data)+"\n")

            # import dữ liệu lấy được từ email lên trang pleiger
            response=mb.pleiger_input(data)

            print(response)

        time.sleep(2)

# Đăng nhập vào mail
mb2 = MailBot("hoaiphong.nguyen@thlsoft.com","123456789a","mail.thlsoft.com")
mb2.login_imap()

thread = Thread(target=threaded_get_new_email, args=(mb2,),daemon=True)
thread.start()

x = input()
while x != 'q':
    x= input()

exit()





