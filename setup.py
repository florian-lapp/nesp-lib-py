import setuptools

setuptools.setup(
    name = 'NESP-Lib',
    description = 'New Era Syringe Pump Library for Python',
    keywords = ['New-Era-Pump-Systems', 'Syringe-Pump'],
    version = '0.3.0',
    url = 'https://github.com/florian-lapp/nesp-lib-py',
    packages = ['nesp_lib'],
    install_requires = ['pyserial'],
    author = 'Florian Lapp',
    author_email = 'e5abed0c@gmail.com'
)