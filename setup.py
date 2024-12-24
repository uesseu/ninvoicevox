from setuptools import setup, find_packages

setup(
    name='ninvoicevox',
    version='0.0.1',
    packages=find_packages(),
    description='Client of voicevox.',
    long_description='''Client of voicevox.
It can use voicevox asynchronously.
It needs voicevox server and this is just a client.''',
    url='https://github.com/uesseu/ninvoicevox',
    author='Shoichiro Nakanishi',
    author_email='sheepwing@kyudai.jp',
    license='MIT',
    zip_safe=False,
    entry_points={
        "console_scripts": [
            "ninvoice=ninvoicevox.main_command:main",
        ]
    },
)
