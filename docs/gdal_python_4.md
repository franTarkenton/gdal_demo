# Using GDAL/OGR with python

## Programming flow / object hierarchy

<IMG src="https://lh3.googleusercontent.com/dGb_JFYJWqgY3kqwRBq_a-8oBWKKCNWgvs2gfMjtlS_vmtx2qoQESAmwQfEa9oR1kEZLzSicpWQLUJbm494OOhgxUSt676o4vpZq9aORPcyThbOjli2wj01Gyd3F4oaeDofMHy_ecJE=w1563-h879-no" width=400>

* Driver (Defines data type, ex, FGDB, shape file, postgis etc)
  * Data Source (Defines source, path, db connection params etc)
    * Layer (A collection of features)
      * Feature (individual row in a table with a geometry)
        * Attributes - tabular goodness
        * Geometry - where?

[Code Demos](gdal_python_code_demo_5.md)