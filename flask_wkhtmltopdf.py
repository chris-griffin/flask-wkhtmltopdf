'''
    Flask-WkHTMLtoPDF

    -----------------

    Convert JavaScript dependent Flask templates into PDFs with wkhtmltopdf.

    :copyright: (c) 2015 by Chris Griffin
    :license: MIT, see LICENSE file for more info

'''

#Backward compatibility for 2.7
from __future__ import absolute_import, division, print_function, unicode_literals
from flask import render_template, make_response
import celery
import subprocess
import os
import tempfile

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

        from flask_wkhtmltopdf import Wkhtmltopdf

        app = Flask(__name__)
        wkhtmltopdf = Wkhtmltopdf(app)

    Then pass the template to the render_template_to_pdf() function. You can 
    pass Jinja2 params just like with render_template()::

        render_template_to_pdf('test.html', download=True, save=False, param='hello')

    Celery, an asynchronous task queue, is highly suggested when using Flask-WkHTMLtoPDF as rendering 
    the PDF can be resource heavy and take an unacceptable amount of time to generate. To 
    enable Celery, set 'WKHTMLTOPDF_USE_CELERY = True' in your Flask app's config. 

    You must add three variables to your Flask app's config::

        WKHTMLTOPDF_BIN_PATH = r'C:\Program Files\wkhtmltopdf\bin'
        PDF_DIR_PATH =  os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static', 'pdf')



    '''
    use_celery = False

    def __init__(self, app=None):
        if app is not None:
            self._init_app(app)

    def _init_app(self, app):
        '''Initalizes the app with Flask-WkHTMLtoPDF.

        :param app: The Flask application object.

        '''

        self.use_celery = app.config.get('WKHTMLTOPDF_USE_CELERY', False)
        self.add_path = app.config.get('WKHTMLTOPDF_BIN_PATH', None)
        self.pdf_dir_path = app.config.get('PDF_DIR_PATH', None)


    #checks to see if condition is true before applying decorator.
    def _maybe_decorate(condition, decorator):
        return decorator if condition else lambda x: x


    @_maybe_decorate(use_celery, celery.task())
    def render_template_to_pdf(self, template_name_or_list, save=False, download=False, **context):
        '''Renders a template from the template folder with the given
        context and produces a pdf. As this can be resource intensive, the function
        can easily be decorated with celery.task() by setting the WKHTMLTOPDF_USE_CELERY to True.
        
        :param template_name_or_list:    The name of the template to be
                                         rendered, or an iterable with template names.
                                         The first one existing will be rendered.
        :param save:    Specifies whether to save the temporary pdf generated. Defaults to False.
        :param download:    Specifies if the pdf should be displayed in the browser
                            or downloaded as an attachment. Defaults to False (in browser).
        :param context:    The variables that should be available in the
                           context of the Jinja2 template.
        '''

        #Get the system's PATH and add wkhtmltopdf to it if necessary
        path = os.getenv("PATH")
        if "wkhtmltopdf" not in path:
            if self.add_path is None:
                raise ValueError('WKHTMLTOPDF_BIN_PATH config variable must be set in the Flask app or added to the OS PATH')
            os.environ["PATH"] += os.pathsep + self.add_path 

        
        #render appropriate template and write to a temp file
        rendered = render_template(template_name_or_list, **context)
        with tempfile.NamedTemporaryFile(suffix='.html', dir=os.path.dirname(__file__), delete=False, mode='w') as temp_html:
            temp_html.write(rendered)

        #Checks to see if the pdf directory exists and generates a random pdf name
        if self.pdf_dir_path is None:
            raise ValueError('PDF_DIR_PATH config variable must be set in the Flask app')
        if not os.path.isdir(self.pdf_dir_path):
            os.makedirs(self.pdf_dir_path)
        with tempfile.NamedTemporaryFile(suffix='.pdf', dir=self.pdf_dir_path, delete=False) as temp_pdf:
            pass        

        #Run wkhtmltopdf via the appropriate subprocess call
        wkhtmltopdfargs = "wkhtmltopdf" + " " + temp_html.name + " " + temp_pdf.name
        
        #A work around for python 2.6
        try:
            subprocess.check_output(wkhtmltopdfargs, shell=True)
        except:
            def check_output(*popenargs, **kwargs):
                process = subprocess.Popen(stdout=subprocess.PIPE, *popenargs, **kwargs)
                output, unused_err = process.communicate()
                retcode = process.poll()
                if retcode:
                    cmd = kwargs.get("args")
                    if cmd is None:
                        cmd = popenargs[0]
                    error = subprocess.CalledProcessError(retcode, cmd)
                    error.output = output
                    raise error
                return output
            subprocess.check_output = check_output
            subprocess.check_output(wkhtmltopdfargs, shell=True)

        #Remove the temporary files created
        os.remove(temp_html.name)

        with open(temp_pdf.name, 'rb') as f:
            binary_pdf = f.read()

        response = make_response(binary_pdf)
        response.headers['Content-Type'] = 'application/pdf'
        if download is True:
            response.headers['Content-Disposition'] = 'attachment; filename=%s.pdf' % temp_pdf.name
        else:
            response.headers['Content-Disposition'] = 'inline; filename=%s.pdf' % temp_pdf.name

        if save is False:
            os.remove(temp_pdf.name)
        
        return response


        






