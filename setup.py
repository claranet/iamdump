from setuptools import setup

setup(
    name="iamdump",
    version="0.0.4",
    author="Raymond Butcher",
    author_email="ray.butcher@claranet.uk",
    url="https://github.com/claranet/iamdump",
    license="MIT License",
    py_modules=["iamdump"],
    entry_points={"console_scripts": ["iamdump=iamdump:cli"]},
    zip_safe=False,
)
