from setuptools import setup, find_packages

install_requires = ["aiohttp", "jinja2", "aiohttp_jinja2", "github3.py"]


setup(
    name="chglg",
    version="0.1",
    packages=find_packages(),
    description="Unified Changelog",
    include_package_data=True,
    zip_safe=False,
    install_requires=install_requires,
    entry_points="""
      [console_scripts]
      chglg-collector = chglg.collector:main
      chglg-web = chglg.web:main
      """,
)
