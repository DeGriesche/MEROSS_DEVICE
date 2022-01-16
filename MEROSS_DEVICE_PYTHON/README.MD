# MEROSS_DEVICE Python

# Deployment 

## Generating distribution archives
Update dependencies
```
pip install --upgrade build
```

Build package
```
python -m build
```

## Uploading the distribution archives¶

Update twine
```
pip install --upgrade twine
```

Upload distribution package
```
python -m twine upload --repository testpypi dist/*
```
