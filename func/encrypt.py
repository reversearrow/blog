import hashlib,binascii,os,hmac,secret_keys

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


def hash_str(s):
	secret = secret_keys.get_secret()
	return hmac.new(secret,s).hexdigest()

def make_secure_val(val):
	return '%s|%s' % (val,hash_str(val))

def check_cookie_val(h):
    s = h.split("|")[0]
    if h == make_secure_val(s):
        return s

