import webapp2,jinja2,os,datetime,urllib2,urllib,time
from func import functions
from func import encrypt
from google.appengine.ext import db

welcome_message = """
<h1> Welcome %(username)s.</h1>
"""
template_dir = os.path.join(os.path.dirname(__file__),'templates')

JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(template_dir),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True)

#template = JINJA_ENVIRONMENT.get_template('newpost.html')


class Handler(webapp2.RequestHandler):
	def write(self, *a, **kw):
		self.response.out.write(*a,**kw)
	def render_str(self,template,**params):
		t = JINJA_ENVIRONMENT.get_template(template)
		return t.render(params)
	def render(self,template,**kw):
		self.write(self.render_str(template, **kw))

class Main(webapp2.RequestHandler):
	def get(self):
		self.redirect("/blog/signup")

class UserDB(db.Model):
	username = db.StringProperty(required=True)
	password = db.StringProperty(required=True)
	salt = db.StringProperty(required=True)
	email = db.StringProperty()

class BlogDB(db.Model):
	subject = db.StringProperty(required=True)
	content = db.TextProperty(required=True)	
	created = db.DateTimeProperty(auto_now_add=True)

class NewPost(Handler):
	def write_newpost(self,subject="",content=""):
		self.render("newpost.html",subject=subject,content=content)
	
	def get(self):
		self.write_newpost()

	def post(self):	
		subject = self.request.get("subject")
		content = self.request.get("content")
		if functions.verify(subject) and functions.verify(content):
			data = BlogDB(subject = subject,content = content)
			data.put()
			keyid = str(data.key().id())
			redirect_uri = "/blog/"+keyid
			self.redirect(redirect_uri)
		else:
			self.write_newpost(subject,content)

class Blog(Handler):
	def get(self):
        	database = BlogDB.all()
		database.order("-created")
		self.render("front.html",database=database)

	def permalink(self,keyid):
		keyid = int(keyid)
		data = BlogDB.all()
		query = data.get().get_by_id(keyid)
		if query:
			self.render("blog.html",subject=query.subject,created=query.created,content=query.content)

class Signup(Handler):
	def write_form(self,username="",email="",error=""):
		self.render("signup.html",username=username,email=email,error=error)

	def get(self):
		self.write_form()

	def validate_input(self,username,password,verify,email):
		if not functions.valid_username(username):
			error = "'%s' is not a valid username." % (username)
			self.write_form(username,email,error)
		elif not functions.valid_password(password):
			error = "Password is not valid is not a valid password."
			self.write_form(username,email,error)
		elif not functions.verify_password(password,verify):
			error = "Verify and Password doesn't match"
			self.write_form(username,email,error)
		elif not functions.valid_email(email):
			error = "'%s' is not an valid email." % (email)
			self.write_form(username,email,error)
		else:
			return True

	def post(self):
		username = self.request.get("username")
		password = self.request.get("password")
		verify = self.request.get("verify")
		email = self.request.get("email")

		if self.validate_input(username,password,verify,email):
			database = UserDB.all()
			query = database.filter('username =', username)
			values = query.get()
			if not values:
				password,salt = encrypt.hashify(password)
				data = UserDB(username=username,password=password,salt=salt,email=email)
				data.put()
				cookie = str("username=%s; Path=/" % username)
				self.response.headers.add_header('Set-Cookie', cookie)
				self.redirect("/blog/welcome")
			else:
				self.write_form(username,error="User already exists")
			

class Welcome(webapp2.RequestHandler):
	def get(self):
		username = self.request.cookies.get('username')
		if username:
			self.response.out.write(welcome_message % ({"username": username}))
		else:
			self.redirect("/blog/signup")



class Login(Handler):
	def write_form(self,username="",password="",error=""):
		self.render("login.html",username=username,password=password,error=error)
	def get(self):
		self.write_form()
	def add_secure_cookie(self,cookie_name,cookie_value):
		cookie = str("%s=%s; Path=/" % (cookie_name,cookie_value))
		return cookie
	
	def post(self):
		username = self.request.get("username")
		password = self.request.get("password")
		database = UserDB.all()
		for i in database:
			print i.username,i.password,i.salt
		query = database.filter('username =', username)
		values = query.get()
		if values:
			if encrypt.verify_hash(password,values.salt,values.password):
				print query.key().id()
				username = encrypt.make_secure_val(username)
				cookie = self.add_secure_cookie('username',username)
				self.response.headers.add_header('Set-Cookie', cookie)
				self.redirect("/blog/welcome")
			else:
				self.write_form(username,error="Password is incorrect")
		else:
			self.write_form(username,error="Username not found")

class Logout(Handler):
	def get(self):
		cookie = str("username=; Path=/")
		self.response.headers.add_header('Set-Cookie',cookie)
		self.redirect("/blog/signup")

app = webapp2.WSGIApplication([('/',Main),
				('/blog/newpost', NewPost),
				('/blog',Blog),
				('/blog/signup',Signup),
				("/blog/welcome",Welcome),
				("/blog/login",Login),
				("/blog/logout",Logout),
				webapp2.Route('/blog/<keyid:[a-zA-Z0-9-_]+>',handler=Blog,
				handler_method="permalink")], debug=True)

