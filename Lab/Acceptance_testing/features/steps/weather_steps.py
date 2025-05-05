from behave import given, when, then
from flask import Flask
from app import create_app  # Assuming you have a Flask app factory
import requests

@given('I open the weather dashboard')
def step_open_dashboard(context):
    # Setup a test client if Flask app
    context.app = create_app()
    context.client = context.app.test_client()
    context.response = context.client.get('/')

@when('I enter "{city}" into the city search field')
def step_enter_city(context, city):
    context.city = city

@when('I click the "Search" button')
def step_click_search(context):
    # Simulate a form POST to your search endpoint
    context.response = context.client.post('/search', data={"city": context.city})
@then('I should see the current weather for "{city}"')
def step_see_weather(context, city):
    print(context.response.get_data(as_text=True))  # ADD THIS
    assert city in context.response.get_data(as_text=True)