from distutils.core import setup
import picasa_utils
setup(name='picasa_utils',
    version=picasa_utils.__version__,
    description='Utility interacting with Picasa.',
    author='Chris Spencer',
    author_email='chrisspen@gmail.com',
    url='https://github.com/chrisspen/picasa-utils',
    license='LGPL License',
    py_modules=['picasa_utils'],
    scripts=['picasa_utils.py'],
    requires=['lockfile', 'gdata'],
    classifiers = [
        "Programming Language :: Python",
        "License :: OSI Approved :: GNU Library or Lesser General Public License (LGPL)",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    platforms=['Linux'],)
