# simplekobold

This is only a tiny implementation.

In the future when implementing an API, maybe make a doc showing a small
scratchpad of information, using short context windows, as you do so. Then
likely a system like langchain could be used to replicate the work
automatically, based on the notes.

## example

```
# import
from simplekobold import SimpleHorde

# construct
horde = SimpleHorde()

# get available models
models = await horde.status_models()

# sort models by availability first and performance second
models.sort(key = lambda model: (model.get('queued'), -model.get('performance')))

# generate text
texts = await horde.generate('Once upon a time,', models=[models[0]['name']], n=1)

# output result
print('Once upon a time', texts[0])
```
