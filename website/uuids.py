from flask import Flask, session

def init_uuids():
    session.permanent = True
    if 'uuids' not in session:
        session['uuids'] = {}

def get_uuids():
    if 'uuids' in session:
        return session['uuids']

def update_uuids(uuid, filename):
    if 'uuids' in session:
        session['uuids'][uuid] = filename
        return session['uuids']

