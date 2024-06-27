import os
from setuptools import find_packages, setup

with open(os.path.join(os.path.dirname(__file__), "README.md")) as readme:
    README = readme.read()

setup(
    name="django-citydb",
    version="0.1.0",
    packages=find_packages(),
    include_package_data=True,
    license="MIT License",
    description="Django GIS based app for virtual discript representation with 3DCityDB and InfluxDB",
    long_description=README,
    url="https://git.rwth-aachen.de/EBC/Team_UES/living-roadmap/django-citydb",
    author="RWTH Aachen University, E.ON Energy Research Center, Institute of Energy Efficient Buildings and Indoor Climate",
    author_email=["premmen@eonerc.rwth-aachen.de"],
)
