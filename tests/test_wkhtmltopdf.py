#Backward compatibility for 2.7
from __future__ import absolute_import, division, print_function, unicode_literals

import unittest

import flask
import celery
from flask_wkhtmltopdf import Wkhtmltopdf
import os



class WkhtmltopdfTests(unittest.TestCase):
    def setUp(self):
        app = flask.Flask(__name__)

        self.wkhtmltopdf_celery_noconfig = Wkhtmltopdf(app)

        app.config['WKHTMLTOPDF_USE_CELERY'] = False
        self.wkhtmltopdf_celery_false = Wkhtmltopdf(app)

        app.config['WKHTMLTOPDF_USE_CELERY'] = True
        self.wkhtmltopdf_celery_true = Wkhtmltopdf(app)

        

    def test_celery_disabled(self):
        self.assertFalse(self.wkhtmltopdf_celery_false.use_celery)

    def test_celery_enabled(self):
        self.assertTrue(self.wkhtmltopdf_celery_true.use_celery)

    def test_celery_default(self):
        self.assertTrue(self.wkhtmltopdf_celery_noconfig.use_celery)

    def test_render_template(self):
        app = flask.Flask(__name__)
        @app.route('/')
        def test():
            rendered = flask.render_template('test.html', test='one-two-three-four')
            return rendered
        rv = app.test_client().get('/')
        self.assertEqual(rv.data, 'one-two-three-four')

    def test_render_pdf(self):
        app2 = flask.Flask(__name__)
        app2.config['WKHTMLTOPDF_USE_CELERY'] = False
        app2.config['WKHTMLTOPDF_BIN_PATH'] = r'C:\Program Files\wkhtmltopdf\bin'
        app2.config['TEMP_FILE_PATH'] = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'temp.html')
        app2.config['PDF_DIR_PATH'] = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'pdf')
        wkhtmltopdf = Wkhtmltopdf(app2)
        @app2.route('/pdf')
        def test():
            wkhtmltopdf.render_template_to_pdf('test.html', test="It worked")
            return 'It worked'
        rv = app2.test_client().get('/pdf')
        self.assertEqual(rv.data, 'It worked')



if __name__ == '__main__':
    unittest.main()

