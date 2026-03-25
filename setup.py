
import random
import string
import logging
import secrets
logging.basicConfig(filename="devaccount.log", level=logging.INFO)

#Generate environment variables
with open(".env", "w") as f:
    f.write("SESSION_KEY="+secrets.token_hex(16)+"\n")
    f.write("PEPPER_PASSWORD="+secrets.token_hex(16))

from server import make_dev_user
#Generate developer account
length = 8
random_string = ''.join(random.choices(string.ascii_letters + string.digits, k=length))
uname = random_string
part1 = ''.join(random.choices(string.ascii_uppercase, k=1))
part2= ''.join(random.choices(string.ascii_letters + string.digits + '_-!?', k=length*2))
part3= ''.join(random.choices(string.digits))
part4= ''.join(random.choices(['_','-','!','?']))
psswd = part1+part2+part3+part4
make_dev_user(username=uname, email=uname+"@gmail.com", password=psswd, userType="M")
logging.info("DevUsername="+uname)
logging.info("DevPassword="+psswd)
#Generate admin account
random_string = ''.join(random.choices(string.ascii_letters + string.digits, k=length))
uname = random_string
part1 = ''.join(random.choices(string.ascii_uppercase, k=1))
part2= ''.join(random.choices(string.ascii_letters + string.digits + '_-!?', k=length*2))
part3= ''.join(random.choices(string.digits))
part4= ''.join(random.choices(['_','-','!','?']))
psswd = part1+part2+part3+part4
make_dev_user(username=uname, email=uname+"@gmail.com", password=psswd, userType="A")
logging.info("AdminUsername="+uname)
logging.info("AdminPassword="+psswd)
#generate user account
random_string = ''.join(random.choices(string.ascii_letters + string.digits, k=length))
uname = random_string
part1 = ''.join(random.choices(string.ascii_uppercase, k=1))
part2= ''.join(random.choices(string.ascii_letters + string.digits + '_-!?', k=length*2))
part3= ''.join(random.choices(string.digits))
part4= ''.join(random.choices(['_','-','!','?']))
psswd = part1+part2+part3+part4
make_dev_user(username=uname, email=uname+"@gmail.com", password=psswd, userType="T")
logging.info("UserUsername="+uname)
logging.info("UserPassword="+psswd)
