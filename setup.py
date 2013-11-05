from setuptools import setup

setup(
    name='log2mq',
    version='1.0.1',
    url='http://git.corp.anjuke.com/gywang/log_mq',
    author='gywang',
    author_email='gywang@anjuke.com',
    packages=['log2mq'],
    platforms='any',
    install_requires=[
        'PyYAML>=3.10',
        'msgpack-python>=0.4.0',
        'pyzmq>=13.1.0',
        'tailer==0.2.1',
    ],

    dependency_links = [
        "http://git.corp.anjuke.com/leichen_sh/pytailer/archive/v0.2.1.zip#egg=tailer-0.2.1"
    ]
)
