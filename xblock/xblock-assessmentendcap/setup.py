from setuptools import setup

setup(
    name='xblock-assessmentendcap',
    version='0.1',
    description='AssessmentEndcap XBlock',
    py_modules=['assessmentendcap'],
    install_requires=['XBlock'],
    entry_points={
        'xblock.v1': [
            'assessmentendcap = assessmentendcap:AssessmentEndcapXBlock',
        ]
    }
)
