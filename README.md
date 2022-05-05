# modelLoader
modelLoader for B.Water Animation Studios pipeline helps to import published MODEL, by all or selected objects, avoid file browsing.

<img src="https://github.com/AlbertoGZ-dev/modelLoader/blob/master/documentation/modelLoader.JPG"></img>

## Setup

#### Manual installation

Place the *modelLoader.py* and *\_\_init\_\_.py* files in a folder named *modelLoader* in your Maya scripts directory and create a python shell button with the following code:

```python
from modelLoader import modelLoader

try:
    md_win.close()
except:
    pass
md_win = modelLoader.modelLoader(parent=modelLoader.getMainWindow())
md_win.show()
md_win.raise_()
```
