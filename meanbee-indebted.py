import webapp2
import jinja2
import os

jinja_environment = jinja2.Environment(loader=jinja2.FileSystemLoader(os.path.dirname(__file__)))

from google.appengine.ext import db
import json

class Indebted(db.Model):
  """Models a poor individual who finds themselves in balance."""
  name = db.StringProperty()
  image = db.StringProperty()
  email = db.EmailProperty()
  balance = db.FloatProperty()

  def decrease_balance(self, amount):
      self.balance -= amount

  def increase_balance(self, amount):
      self.balance += amount

class Transaction(db.Model):
    reference = db.StringProperty()
    buyer_id = db.IntegerProperty()
    buyee_ids = db.ListProperty(item_type=int)
    amount = db.FloatProperty()
    date = db.DateTimeProperty(auto_now_add=True)


def loadTransactions(count=False):
    transactions = []
    transactionModels = None
    if count:
        transactionModels = Transaction.all().order('-date').fetch(count)
    else:
        transactionModels = Transaction.all().order('-date')

    for transactionModel in transactionModels:
        transaction = {
            'buyer': Indebted.get_by_id(transactionModel.buyer_id),
            'buyees': map(lambda x:Indebted.get_by_id(x), transactionModel.buyee_ids),
            'reference': transactionModel.reference,
            'amount': transactionModel.amount,
            'date': transactionModel.date
        }
        transactions.append(transaction)
    return transactions


class HistoryPage(webapp2.RequestHandler):
    def get(self):
        template_values = {
            'transactions': loadTransactions()
        }

        template = jinja_environment.get_template('history.html')
        self.response.out.write(template.render(template_values))


class MainPage(webapp2.RequestHandler):
  def get(self):
      transactions =  loadTransactions(10)
      template_values = {
          'indebted': Indebted.all(),
          'transactions': transactions
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
            i.balance = 0.0
            i.put()
            self.response.out.write('{status: "OK"}')
        else:
            self.response.out.write('{status: "FAIL", reason: "Name, email or image not provided. %s, %s, %s"}' % (name, email, image))


class AddTransaction(webapp2.RequestHandler):
    def update_balances(self, amount, buyee_ids, buyer_id):
        balance_modification = amount / len(buyee_ids)
        buyer = Indebted.get_by_id(buyer_id)
        buyer.increase_balance(balance_modification)
        buyer.put()
        for buyee_id in buyee_ids:
            if buyee_id == buyer_id:
                # Ignore charging the buyer
                continue
            buyee = Indebted.get_by_id(buyee_id)
            buyee.decrease_balance(balance_modification)
            buyee.put()

    def add_transaction(self, buyee_ids, buyer_id, reference, amount):
        transaction = Transaction()
        transaction.buyer_id = int(buyer_id)
        transaction.buyee_ids = buyee_ids
        transaction.reference = reference
        transaction.amount = amount
        transaction.put()

    def post(self):
        buyer_id   = int(self.request.get("buyer"))
        amount     = float(self.request.get("amount"))
        reference  = self.request.get("reference")
        buyee_ids  = map(lambda x:int(x), self.request.get("buyees", allow_multiple=True))

        self.update_balances(amount, buyee_ids, buyer_id)
        self.add_transaction(buyee_ids, buyer_id, reference, amount)

class AddTransactionWithJson(AddTransaction):
    def post(self):
        self.response.headers['content-type'] = 'application/json'
        status = {'status': 'OK'}
        try:
            super(AddTransactionWithJson, self).post()
        except Exception as e:
            status['status'] = 'FAIL'
            status['reason'] = e.value


        self.response.out.write(json.dumps(status))



class AddTransactionWithRedirect(AddTransaction):
    def post(self):
        super(AddTransactionWithRedirect, self).post()

        self.redirect('/')

class GetIndebtedInfo(webapp2.RequestHandler):
    def get(self):
        indebted = Indebted.all()
        jsonArray = []
        for i in indebted:
            jsonArray.append({
                'name': i.name,
                'email': i.email,
                'id': i.key().id(),
                'balance': i.balance,
                'image': i.image
            })
        self.response.headers['content-type'] = 'application/json'
        self.response.out.write(json.dumps(jsonArray))



app = webapp2.WSGIApplication([
    ('/', MainPage),
    ('/history', HistoryPage),
    ('/add_transaction', AddTransactionWithRedirect),
    ('/api/add_transaction', AddTransactionWithJson),
    ('/api/get_indebted_info', GetIndebtedInfo),
    ('/create_user', CreateUser),
], debug=True)



