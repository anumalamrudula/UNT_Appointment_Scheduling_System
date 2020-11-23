import os

class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or b"\xcey\x99\x89b\x8f\xb6D\xaa_]'VL\x19j"   
    DB_URI = "mongodb+srv://test:test@cluster0.bh7cy.mongodb.net/Appointment_Scheduling?retryWrites=true&w=majority"
