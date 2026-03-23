from server import make_dev_user
import random
import string
import logging
import secrets
logging.basicConfig(filename="devaccount.log", level=logging.INFO)

#Generate developer account
length = 8
random_string = ''.join(random.choices(string.ascii_letters + string.digits, k=length))
uname = random_string
part1 = ''.join(random.choices(string.ascii_uppercase, k=1))
part2= ''.join(random.choices(string.ascii_letters + string.digits + '@:;!?', k=length*2))
part3= ''.join(random.choices(string.digits))
part4= ''.join(random.choices(['@',':',';','!','?']))
psswd = part1+part2+part3+part4
make_dev_user(uname, psswd)
logging.info("Username:"+uname)
logging.info("Password:"+psswd)

#Generate environment variables
with open("")