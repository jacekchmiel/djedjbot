from setuptools import setup

setup(
    name='dj',
    scripts='dj.py',
    install_requires=['requests', 'spotipy', 'termcolor'],
    use_scm_version=True,
    setup_requires=['setuptools_scm']
)
