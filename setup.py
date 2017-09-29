from setuptools import setup

setup(
    name='djedjbot',
    scripts='djedjbot.py',
    install_requires=['requests', 'spotipy'],
    use_scm_version=True,
    setup_requires=['setuptools_scm']
)
