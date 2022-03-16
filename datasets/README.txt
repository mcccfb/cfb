
Follow this:

https://packaging.python.org/en/latest/guides/installing-using-pip-and-virtual-environments/

To start the env:

$ python3 -m venv env
$ source env/bin/activate

Then install packages you need for this env:

$ pip3 install cfbd
$ pip3 install --upgrade pip

To get out of the environment:

$ deactivate

To get back in:

$ source env/bin/activate

Many libs needed for plotly and extras:

$ pip3 install plotly==5.5.0
$ pip3 install -U kaleido
$ pip3 install pandas
$ pip3 install statsmodels

Full API docs on plotly :

https://plotly.com/python-api-reference/generated/plotly.express.scatter

Man page intro docs:

https://plotly.com/python/line-and-scatter/
