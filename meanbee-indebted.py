import webapp2
import jinja2
import os

jinja_environment = jinja2.Environment(loader=jinja2.FileSystemLoader(os.path.dirname(__file__)))

from google.appengine.ext import db

class Indebted(db.Model):
  """Models a poor individual who finds themselves in debt."""
  name = db.StringProperty();
  image = db.StringProperty();
  email = db.EmailProperty();
  debt = db.FloatProperty();

class MainPage(webapp2.RequestHandler):
  def get(self):
      template_values = {
          'indebted': Indebted.all()
      }

      template = jinja_environment.get_template('index.html')
      self.response.out.write(template.render(template_values))

class CreateUser(webapp2.RequestHandler):
    def post(self):
        self.response.headers['Content-Type'] = 'application/json'

        name  = self.request.get('name')
        email = self.request.get('email')
        image = self.request.get('image')

        if name and email and image:
            i = Indebted()
            i.name = name
            i.email = email
            i.image = image
            i.debt = 0.0
            i.put()
            self.response.out.write('{status: "OK"}')
        else:
            self.response.out.write('{status: "FAIL", reason: "Name, email or image not provided. %s, %s, %s"}' % (name, email, image))







app = webapp2.WSGIApplication([
    ('/', MainPage),
    ('/create_user', CreateUser),
], debug=True)



