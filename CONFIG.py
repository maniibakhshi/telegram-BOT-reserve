import os
admins = eval(os.environ.get("admins", "1690931198"))
Channel_cid = int(os.environ.get("Channel_cid", -1003182326354))
databasename = os.environ.get('databasename', 'academy_78')
default_card = os.environ.get('default_card','6037-9975-4948-7057')
default_amount = os.environ.get('default_amount','300,000')
groom_amount = os.environ.get('groom_amount','1,000,000')
skin_amount = os.environ.get('skin_amount','500,000')
config = {
    'user': os.environ.get('user', 'root'),
    'password': os.environ.get('password', 'password'),
    'host': os.environ.get('host', 'localhost'),
    'database': databasename
}

logfile = os.environ.get('logfile', 'project.log')

BOT_TOKEN = os.environ.get('TOKEN', '8209284106:AAEFMmlwl4ZUrMFymPdqxxLos9r_-30sEsA')
