import os
import sys

import numpy as np
import dill
import yaml
from pandas import DataFrame

from src.exception import MyException
from src.logger import logging

def read_yaml_file(file_path: str) -> dict:
    try:
        with open(file_path, "r") as yaml_file:
            return yaml.safe_load(yaml_file)
    except Exception as e:
        raise MyException(e, sys)
    

def write_yaml_file(file_path: str, content: object, replace: bool = False) -> None:
    try:
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        if replace:
            mode = "w"
        else:
            mode = "a"
        with open(file_path, mode) as yaml_file:
            yaml.dump(content, yaml_file)
    except Exception as e:
        raise MyException(e, sys)
    
def load_object(file_path: str) -> object:
    try:
        with open(file_path, "rb") as file_obj:
            return dill.load(file_obj)
    except Exception as e:
        raise MyException(e, sys)
    
def save_object(file_path: str, obj: object) -> None:
    try:
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, "wb") as file_obj:
            dill.dump(obj, file_obj)
    except Exception as e:
        raise MyException(e, sys)
    

def save_numpy_array(file_path: str, array: np.ndarray) -> None:
    try:
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        np.save(file_path, array)
    except Exception as e:
        raise MyException(e, sys)
    
def load_numpy_array(file_path: str) -> np.ndarray:
    try:
        return np.load(file_path)
    except Exception as e:
        raise MyException(e, sys)