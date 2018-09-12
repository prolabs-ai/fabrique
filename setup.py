from setuptools import setup

setup(name='fabrique',  
        version='0.1.56',
        description='Fabrique local environment',
        long_description="""
Fabrique local environment allows you to test ML pipelines locally, before
submitting them to Fabrique
""",
        url='http://www.fabrique.ai',
        author='Pavel Velikhov',
        author_email='pavel.velikhov@prolabs.ai',
        license='MIT',
        keywords='ML pipeline',
        packages=['fabrique'],
 	package_dir = {'': '.'},
        install_requires=['jsonschema>=2.6.0'],
        scripts = ['fabrique/bin/fabrique_pipeline.py'],
        classifiers = [ 
          'Development Status :: 3 - Alpha',
          'License :: OSI Approved :: MIT License'
        ])
