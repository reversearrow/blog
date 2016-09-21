import webapp2,jinja2,os


template_dir = os.path.join(os.path.dirname(__file__),'templates')

JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(template_dir),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True)

template = JINJA_ENVIRONMENT.get_template('newpost.html')

class MainPage(webapp2.RequestHandler):
    def get(self):
        self.response.headers['Content-Type'] = 'text/plain'
        self.response.write('Hello, Udacity!')

class NewPost(webapp2.RequestHandler):
	def get(self):
		self.response.write(template.render())

	def post(self):
		self.response.write(template.render())



app = webapp2.WSGIApplication([('/', MainPage),('/newpost', NewPost)], debug=True)
