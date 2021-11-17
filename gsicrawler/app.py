#!/usr/bin/env python
import connexion
import logging
import os
from connexion.resolver import RestyResolver
from flask import redirect

logging.basicConfig(level=logging.INFO)

def go_to_ui():
    return redirect('/api/v1/ui')

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app = connexion.App(__name__)
    app.app.add_url_rule('/', 'index', go_to_ui)
    app.add_api('gsicrawler_api.yaml', arguments={'title': 'GSICrawler API'}, resolver=RestyResolver('gsicrawler.controllers'))

    from gsicrawler import tasks
    app.app.tasks = tasks

    app.run(host='0.0.0.0',port=port, debug=os.environ.get('DEBUG', False))
