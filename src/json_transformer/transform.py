import argparse
import json
import os

from enum import Enum
from typing import Dict, List, Union

class JsonType(Enum):
    Json = dict
    List = list
    String = str
    Int = int
    Float = float
    Bool = bool

class TransformDict(dict):

    def __init__(self, *args, **kwargs):
        if args:
            super().__init__(zip(range(len(args)), args))
            self.__json_type__ = JsonType.List
        else:
            super().__init__(**kwargs)
            self.__json_type__ = JsonType.Json

    def __getattr__(self, key):
        assert isinstance(key, (str, bool, int, float, dict, list))
        if key not in self.keys():
            super().__setitem__(key, TransformDict())
        value = super().__getitem__(key)
        if isinstance(value, (str, bool, int, float, TransformDict)):
            return value
        if isinstance(value, list):
            return TransformDict(*value)
        if isinstance(value, dict):
            return TransformDict(**value)
        raise TypeError(f"Unhandled value type {type(value)}")

    def __getitem__(self, keys):
        if isinstance(keys, tuple):
            value_dict = TransformDict()
            for key in keys:
                value_dict[key] = self.__getitem__(key)
            return value_dict

        key = keys
        assert isinstance(key, (str, bool, int, float, tuple))
        value = super().__getitem__(key)
        if isinstance(value, (str, bool, int, float, TransformDict)):
            return value
        if isinstance(value, list):
            return TransformDict(*value)
        if isinstance(value, dict):
            return TransformDict(**value)


    def __setattr__(self, key, value):
        if key == '__json_type__':
            return super().__setattr__(key, value)
        self.__setitem__(key, value)

    def __setitem__(self, key, value):
        assert isinstance(key, (str, bool, int, float))
        if isinstance(key, int):
            self.__json_type__ = JsonType.List
        else:
            try:
                key = eval(key, {}, {})
            except NameError:
                ...
        super().__setitem__(key, value)

    def to_json_obj(self):
        if self.__json_type__ == JsonType.Json:
            result = dict()
            for key, value in self.items():
                if isinstance(value, TransformDict):
                    result[key] = value.to_json_obj()
                else:
                    result[key] = value
            return result
        elif self.__json_type__ == JsonType.List:
            # TODO: handle exception
            indexes = [int(k) for k in self.keys()]
            results = []
            for i in indexes:
                value = self[i]
                results.append(value.to_json_obj() if isinstance(value, TransformDict) else value)
            return results

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("from_file", type=str)
    parser.add_argument("-f", "--code-file", type=str, default="")
    parser.add_argument("-o", "--output", type=str, default="transform_results")
    parser.add_argument("-t", action='append', dest="transformers")

    arguments = parser.parse_args()
    if arguments.code_file:
        with open(arguments.code_file, encoding='utf-8') as f:
            arguments.transformers = f.readlines()
    return arguments

def transform_json(src: dict, transformers: List[str]) -> Dict:
    src = TransformDict(**src)
    dst = TransformDict()
    for transformer in transformers:
        dst.messages[0] = src.observations[0].input[0]
        exec(transformer)
    return dst.to_json_obj()

def transform_json_list(source_json_list: List[Dict], transformers: List[str]) -> List[Dict]:
    transform_results = []
    for src in source_json_list:
        try:
            dst = transform_json(src, transformers)
            transform_results.append(dst)
        except Exception:
            continue
    return transform_results

def load_json_obj(file_or_dir_path: str):
    if os.path.isfile(file_or_dir_path):
        with open(file_or_dir_path, encoding='utf-8') as f:
            obj = json.load(f)
        return obj

    objs = []
    for file_name in os.listdir(file_or_dir_path):
        with open(os.path.join(file_or_dir_path, file_name), encoding='utf-8') as f:
            obj = json.load(f)
        objs.append(obj)
    return objs


def save_json_obj(file_or_dir_path: str, obj: Union[Dict, List[Dict]]):
    if '.' in file_or_dir_path:
        with open(file_or_dir_path, 'w', encoding='utf-8') as f:
            f.write(json.dumps(obj, ensure_ascii=False, indent=2))
        return
    assert isinstance(obj, list)
    for i, item in enumerate(obj):
        os.makedirs(file_or_dir_path, exist_ok=True)
        with open(os.path.join(file_or_dir_path, f'{i}.json'), 'w', encoding='utf-8') as f:
            f.write(json.dumps(item, ensure_ascii=False, indent=2))


def main():
    args = parse_args()
    json_obj = load_json_obj(args.from_file)
    if isinstance(json_obj, list):
        save_json_obj(args.output, transform_json_list(json_obj, args.transformers))
    else:
        save_json_obj(args.output, transform_json(json_obj, args.transformers))


if __name__ == '__main__':
    main()
