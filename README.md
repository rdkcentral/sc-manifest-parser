# sc-manifest-parser

A library for reading and writing SC repo manifests.

## Requirements

SC officially supports Python 3.10+

## Installation

Run command in terminal:

`pip install git+ssh://git@github.com/comcast-sky/sc-manifest-parser@master`

## Usage

### Load a Manifest
```python
from sc_manifest_parser import ScManifest

manifest = ScManifest("/path/to/manifest.xml")
```

Or if you have already init'd your repo:

`manifest = ScManifest.from_repo_root("/path/to/repo/.repo")`

### Access Elements

```
projects = manifest.projects
for proj in projects:
    print(proj.name)
```

Some other elements to access include:
```
manifest.remotes
manifest.post_sync_scripts
manifest.defaults
```

### Read Element Attributes

The attributes in the xml are the ManifestElementInterfaces attributes:

`<project name="example.git" path="ex_path" revision="02c940338192e4ff930abd63ac44d3e737f78287">`

- project.name == "example.git"
- project.path == "ex_path"
- project.revision == "02c940338192e4ff930abd63ac44d3e737f78287"

### Modify Attributes

- Change value: `project.name = "new_name.git"`
- Delete value: `del project.name`

### Add or Remove Elements
```
# Add child
proj.add_child("annotation", {"name": "FOO", "value": "BAR", "attribute": "value"})

# Delete an element
proj.remove()
```

### Write Changes Back

`manifest.write()`

