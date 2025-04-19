# json-transformer

## Installation

```bash
pip install json-transformer
```

## Usage

### Create a transformer file

```python
# chat_data_transformer.py
from json_transformer import src, dst

dst.messages[0] = src.observations[0].input[0]
dst.messages[1] = src.observations[0].output['role', 'content']
```

### Transform Json File

```bash
transjson {source_json_file} -f chat_data_transformer.py 
```
