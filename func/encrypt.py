import hashlib,binascii,os,hmac


def hashify(password,salt=""):
	hash_algorith = "sha256"
	password = password
	if salt == "":
		salt = os.urandom(16).encode("hex")
		dk = hashlib.pbkdf2_hmac('sha256', password, salt, 100000)
        	binary = binascii.hexlify(dk)
        	return binary,salt
	else:
		salt = salt
		dk = hashlib.pbkdf2_hmac('sha256', password, salt, 100000)
		binary = binascii.hexlify(dk)
		return binary

def verify_hash(password,salt,stored_hash):
	calculated_hash = hashify(password,salt)
	if calculated_hash == stored_hash:
		return True
	else:
		return False

def make_secure_val(val):
	return '%s|%s' % (val,hmac.new(secret,val).hexdigest())

def check_secure_val(secure_val):
	val = secure_val.split('|')[0]
	if secure_val == val:
		return val

