import cgi,re
USER_RE = re.compile(r"^[a-zA-Z0-9_-]{3,20}$")
PASSWORD_RE = re.compile("^.{3,20}$")
EMAIL_RE = re.compile("^[\S]+@[\S]+.[\S]+$")

def verify(text):
	if text and not text.isspace():
		return True
		
def valid_username(username):
    if username:
	return USER_RE.match(username)

def valid_password(password):
    if password:
	return PASSWORD_RE.match(password)

def valid_email(email):
	if email:
		return EMAIL_RE.match(email)
	else:
		return True


def verify_password(password,verify):
    if password and verify:
	if password == verify:
		return True
    	else:
        	return False
