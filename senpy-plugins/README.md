# liwc-gsi

A plugin for LIWC 2015 dictionary. A Jupyter Notebook is also provided showing how to use the liwc library and the senpy plugin.

## Using this plugin

1. Clone this repo
2. Create a data folder: ``` mkdir data ```
3. Put the dictionary ``LIWC2015Dictionary.dic`` inside the data folder
4. Run Senpy with ``senpy -f .``

## Docker

You can also create a docker image using the provided Dockerfile:
```
docker build . -t senpy-liwc
docker run -p 5000:5000 senpy-liwc

```
