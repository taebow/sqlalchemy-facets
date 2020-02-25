from setuptools import setup, find_packages

install_requires = [
    "sqlalchemy",
    "psycopg2-binary"
]

dev_requires = [
    "pytest",
    "pytest-cov",
    "factory-boy",
    "sphinx",
    "sphinx-autodoc-typehints",
    "sphinx-rtd-theme"
]

setup(
    name="sqlalchemy-facets",
    version="0.0.1",
    author="Thibaut Frain",
    author_email="thibaut.frain@gmail.com",
    description="Faceted filters for SQL Alchemy",
    packages=find_packages(exclude=["tests"]),
    include_package_data=True,
    install_requires=install_requires,
    extras_require={"dev": dev_requires}
)
