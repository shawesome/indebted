import webapp2
import jinja2
import os

jinja_environment = jinja2.Environment(loader=jinja2.FileSystemLoader(os.path.dirname(__file__)))

from google.appengine.ext import db

class Indebted(db.Model):
  """Models a poor individual who finds themselves in debt."""
  name = db.StringProperty();
  email = db.EmailProperty();
  debt = db.FloatProperty();

class MainPage(webapp2.RequestHandler):
  def get(self):
      template_values = {
          'indebted': Indebted.all()
      }

      template = jinja_environment.get_template('index.html')
      self.response.out.write(template.render(template_values))

app = webapp2.WSGIApplication([('/', MainPage)],
                              debug=True)

