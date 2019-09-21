from setuptools import setup
try:
    from pip._internal.req import parse_requirements
except ImportError:
    from pip.req import parse_requirements

install_reqs = parse_requirements("requirements.txt", session=False)

reqs = [str(ir.req) for ir in install_reqs]

setup(
    name='PSMProcessing',
    version='1.0.0',
    packages=[
        'PSMProcessing'
    ],
    url='https://github.com/cemel-jhu/PSM-Image-Processing',
    license='MIT',
    author='Dylan Madisetti',
    author_email='madisetti@jhu.edu',
    description=('Methods for determining PSM propagation speed and emybro '
        'width in micro-pillar loading experiments.'),
    install_requires=reqs
)
