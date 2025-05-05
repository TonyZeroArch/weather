import os
from flask import Flask

app = Flask(__name__, root_path=os.getcwd())

@app.route('/')
def home():
    return "Welcome"

client = app.test_client()

@given('I open the homepage')
def step_impl(context):
    context.response = client.get('/')

@then('I should see "{message}"')
def step_impl(context, message):
    assert message in context.response.get_data(as_text=True)