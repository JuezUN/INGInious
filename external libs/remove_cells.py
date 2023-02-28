def prepare_notebook(notebook_path, notebook_result_path):
    import nbformat
    nb = nbformat.read(notebook_path, as_version=nbformat.NO_CONVERT)

    for i, c in enumerate(nb.cells):
        if ("## TEACHER" in c.source):
            nb.cells.pop(i)
        
        if "## KEEPOUTPUT" not in c.source:
            nb.cells[i].outputs = []

    nbformat.write(nb, notebook_result_path)