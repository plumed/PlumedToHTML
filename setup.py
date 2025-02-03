import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()


setuptools.setup(
     name='PlumedToHTML',  
     version='0.101',
     author="Gareth Tribello",
     author_email="gareth.tribello@gmail.com",
     description="A package for creating pretified HTML for PLUMED files",
     long_description=long_description,
     long_description_content_type="text/markdown",
     url="https://github.com/plumed/PlumedToHTML",
     packages=setuptools.find_packages(),
     classifiers=[
         "Programming Language :: Python :: 3",
         "License :: Freely Distributable",
         "Operating System :: OS Independent",
     ],
     install_requires=['lxml','pygments','requests','bs4'],
    # This adds the assets that PlumedToHTML.get_html_header() asks for ()
     data_files=[('PlumedToHTML', ['PlumedToHTML/assets/header.html'])],
     include_package_data=True,
 )
# print(setuptools.find_packages())
