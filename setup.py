import os
from setuptools import setup, find_packages


PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))

setup(name='paasbakeoff',
	version='1.0',
	author='Nate Aune',
	author_email='nate@appsembler.com',
	url='https://github.com/appsembler/paasbakeoff',
	packages=find_packages(),
	include_package_data=True,
	description='Example Mezzanine CMS deploy to OpenShift PaaS',
	install_requires=open('%s/mywebsite/requirements/project.txt' % os.environ.get('OPENSHIFT_REPO_DIR', PROJECT_ROOT)).readlines(),
#	install_requires=['Mezzanine==1.2.4',],
)

