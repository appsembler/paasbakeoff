from setuptools import setup, find_packages

setup(name='paasbakeoff',
	version='1.0',
	author='Nate Aune',
	author_email='nate@appsembler.com',
	url='https://github.com/appsembler/paasbakeoff',
	packages=find_packages(),
	include_package_data=True,
	description='Example Mezzanine CMS deploy to OpenShift PaaS',
	install_requires=open('mywebsite/requirements/project.txt').readlines(),
)