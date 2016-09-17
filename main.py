import webapp2,jinja2,os,functions,datetime,urllib2,urllib,time
from google.appengine.ext import db

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


app = webapp2.WSGIApplication([('/blog/newpost', NewPost),('/blog',Blog),webapp2.Route('/blog/<keyid:[a-zA-Z0-9-_]+>',handler=Blog,handler_method="permalink")], debug=True)



