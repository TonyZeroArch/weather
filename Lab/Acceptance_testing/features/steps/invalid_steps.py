from behave import given, when, then
from flask import Flask
from app import create_app  # assuming you have an app factory
import requests

@then('I should see an error message "City not found"')
def step_see_error_message(context):
    page_text = context.response.get_data(as_text=True)
    print(page_text)  # Useful for debugging
    assert "City not found" in page_text