import webapp2,jinja2,os,functions,datetime,urllib2,urllib,time
from functions import valid_username, valid_password, valid_email,verify_password
from google.appengine.ext import db

user_signup_form = """
<h2>User Signup</h2>
<form method="POST">
<label> Username <input type = "text" name = "username" value = "%(username)s"></input></label> <br>
<label> Password <input type = "password" name = "password" value = ""> </input></label> <br>
<label> Verify <input type = "password" name = "verify"> </input></label> <br>
<label> Email <input type = "text" name = "email" value = "%(email)s"> </input></label> <br>
<input type="submit">
<h2> %(error)s </h2>
"""

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

class Signup(webapp2.RequestHandler):
	def write_form(self,username="",password="",email="",error=""):
		self.response.write(user_signup_form % ({"username":username,"password":password,"email":email,"error":error}))

	def get(self):
		self.write_form()

	def validate_input(self,username,password,verify,email):
		if not valid_username(username):
			error = "'%s' is not a valid username." % (username)
			self.write_form(username,password,email,error)
		elif not valid_password(password):
			error = "Password is not valid is not a valid password."
			self.write_form(username,password,email,error)
		elif not verify_password(password,verify):
			error = "Verify and Password doesn't match"
			self.write_form(username,password,email,error)
		elif not valid_email(email):
			error = "'%s' is not an valid email." % (email)
			self.write_form(username,password,email,error)
		else:
			self.redirect("/unit2/welcome?username=" + username)

	def post(self):
		username = self.request.get("username")
		password = self.request.get("password")
		verify = self.request.get("verify")
		email = self.request.get("email")

		self.validate_input(username,password,verify,email)


class Welcome(webapp2.RequestHandler):
	def get(self):
		username = self.request.get("username")
		if valid_username(username):
			self.response.out.write(welcome_message % ({"username": username}))
		else:
			self.redirect("/unit2/signup")



app = webapp2.WSGIApplication([('/blog/newpost', NewPost),('/blog',Blog),('/blog/signup',Signup),("/blog/welcome",Welcome),webapp2.Route('/blog/<keyid:[a-zA-Z0-9-_]+>',handler=Blog,handler_method="permalink")], debug=True)



