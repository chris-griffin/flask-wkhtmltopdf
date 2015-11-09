'''
    Flask-WkHTMLtoPDF

    -----------------

    Convert JavaScript dependent Flask templates into PDFs with wkhtmltopdf.

    :copyright: (c) 2015 by Chris Griffin
    :license: MIT, see LICENSE file for more info

'''

#Backward compatibility for 2.7
from __future__ import absolute_import, division, print_function, unicode_literals
from flask import render_template
import celery
import subprocess
import os

class Wkhtmltopdf(object):
    '''Wkhtmltopdf class container to use the robust wkhtmltopdf library which is 
    capable of generating a PDF from HTML, CSS, and JavaScript using a modified
    WebKit engine. This extension allows you to easily incorporate this functionality
    into your Flask app.

    In addition to the dependencies automatically installed, you must manually 
    download the appropriate wkhtmltopdf command line tool from 
    http://wkhtmltopdf.org/downloads.html

    The main function render_template_to_pdf() works similar to Flask's built-in 
    render_template() function and in fact utilizes some of the same underlying 
    functions. However, as the name suggests, it will return a pdf instead of 
    a rendered webpage.

    To initialize, pass your flask app's object to Flask-WkHTMLtoPDF::

        import wkhtmltopdf

        app = Flask(__name__)
        wkhtmltopdf = Wkhtmltopdf(app)

    Then pass the template to the render_template_to_pdf() function. You can 
    pass Jinja2 params just like with render_template()::

        render_template_to_pdf('test.html', param='hello')

    Celery, an asynchronous task queue, is enabled by default in Wkhtmltopdf as rendering 
    the PDF can be resource heavy and take an unacceptable amount of time to generate. To 
    override this default, set 'WKHTMLTOPDF_USE_CELERY = False' in your Flask app's config. 

    You must add three variables to your Flask app's config::

        WKHTMLTOPDF_BIN_PATH = r'C:\Program Files\wkhtmltopdf\bin'
        TEMP_FILE_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'temp.html')
        PDF_DIR_PATH =  os.path.join(os.path.dirname(os.path.abspath(__file__)), 'pdf')



    '''
    use_celery = False

    def __init__(self, app=None):
        if app is not None:
            self.init_app(app)

    def init_app(self, app):
        '''Initalizes the app with Flask-WkHTMLtoPDF.

        :param app: The Flask application object.

        '''

        self.use_celery = app.config.get('WKHTMLTOPDF_USE_CELERY', True)
        self.add_path = app.config.get('WKHTMLTOPDF_BIN_PATH', None)
        self.temp_file_path = app.config.get('TEMP_FILE_PATH', None)
        self.pdf_dir_path = app.config.get('PDF_DIR_PATH', None)


    #checks to see if condition is true before applying decorator.
    def maybe_decorate(condition, decorator):
        return decorator if condition else lambda x: x


    @maybe_decorate(use_celery, celery.task())
    def render_template_to_pdf(self, template_name_or_list, **context):
        '''Renders a template from the template folder with the given
        context and produces a pdf. As this can be resource intensive, the function
        is by default decorated with celery.task(). Therefore, Celery needs to be 
        installed. To disable Celery set the WKHTMLTOPDF_USE_CELERY config to False.
        
        :param template_name_or_list:    The name of the template to be
                                         rendered, or an iterable with template names.
                                         The first one existing will be rendered.
        :param context:    The variables that should be available in the
                           context of the Jinja2 template.
        '''
        rendered = render_template(template_name_or_list, **context)
        with open(self.temp_file_path, "wb") as temp:
            temp.write(rendered)

        #Get the system's PATH and add wkhtmltopdf to it if necessary
        path = os.getenv("PATH")
        if "wkhtmltopdf" not in path:
            if self.add_path is None:
                raise ValueError('WKHTMLTOPDF_BIN_PATH config variable must be set in the Flask app')
            os.environ["PATH"] += os.pathsep + self.add_path

        #Get the appropriate file paths
        if self.temp_file_path is None:
            raise ValueError('TEMP_FILE_PATH config variable must be set in the Flask app')
        
        if self.pdf_dir_path is None:
            raise ValueError('PDF_DIR_PATH config variable must be set in the Flask app')
        self.pdf_file_path = os.path.join(self.pdf_dir_path, 'temp.pdf')

        #Run wkhtmltopdf via the appropriate subprocess call
        wkhtmltopdfargs = "/C wkhtmltopdf" + " " + self.temp_file_path + " " + self.pdf_file_path
        subprocess.check_output(['cmd', wkhtmltopdfargs])


