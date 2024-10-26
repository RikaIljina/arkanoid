import tomllib
import pathlib
import os

conf = pathlib.Path(__file__).parent / 'config.toml'

with open(conf, 'rb') as f:
    config = tomllib.load(f)
print(config)