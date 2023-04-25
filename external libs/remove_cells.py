def prepare_notebook(notebook_path, notebook_name,
                     colab=False):
    '''
    If you have used the TEACHER or KEEPOUTPUT pragmas, you can remove teacher cells 
    and erase all outputs from cells without keepoutput pragma using this method.
    
            Parameters:
                    notebook_path: String with the original notebook location path.
                    notebook_name: String with the original notebook filename.
                    colab: Boolean by default false. It indicates if you are using the 
                           method from a colab environment or locally. 
                           If it is True, it will mount your google drive in the colab environment, 
                           it will ask for authorization, and it will search the running notebook 
                           on the location indicated by the first parameter on the mounted drive.
                           

            This method writes the prepared notebook on: notebook_path + 'Student_' +  notebook_name
    '''
    import os

    locations = []
    name = ""
    if colab:
        import requests
        import urllib.parse
        import google.colab

        mount_dir = '/content/drive'
        google.colab.drive.mount(mount_dir)

        def find_notebook(name):
            paths = [os.path.join(mount_dir, 'MyDrive', notebook_path)]
            for path in paths:
                for dirpath, subdirs, files in os.walk(path):
                    for file in files:
                        if file == name:
                            return os.path.join(dirpath, file)

        def locate_nb(set_singular=True):
            found_file = ""
            colab_ip = "172.28.0.12"
            colab_port = 9000
            nb_address = f"http://{colab_ip}:{colab_port}/api/sessions"
            response = requests.get(nb_address).json()
            name = urllib.parse.unquote(response[0]['name'])
            dir_candidate = []
            found_file = find_notebook(name)
            if len(found_file) > 0:
                nb_dir = os.path.dirname(found_file)
                dir_candidate.append(nb_dir)
                if set_singular:
                    print('Singular location found, setting directory')
                    os.chdir(dir_candidate[0])
            elif not found_file:
                print('Notebook file name not found.')
            # elif len(found_file) > 1:
            #    print('Multiple matches found, returning list of possible locations.')
            #    dir_candidate = [os.path.dirname(f) for f in found_file]
            return dir_candidate, name
        locations, name = locate_nb()
        notebook_path = os.path.join(locations[0], name)
        notebook_result_path = locations[0]
        notebook_result_name = os.path.join(
            notebook_result_path, 'Student_' + name)
    else:
        notebook_result_name = os.path.join(
            notebook_path, 'Student_' + notebook_name)
        notebook_path = os.path.join(notebook_path, notebook_name)

    import nbformat

    nb = nbformat.read(notebook_path, as_version=nbformat.NO_CONVERT)
    new_cells = []
    for cell in nb.cells:
        outputs = []
        if "## TEACHER" in cell.source or "##TEACHER" in cell.source:
            continue

        if "## KEEPOUTPUT" in cell.source or "##KEEPOUTPUT" in cell.source:
            outputs = cell["outputs"]
        cell["outputs"] = outputs
        new_cells.append(cell)
    nb.cells = new_cells

    print("Student Notebook saved on {0}".format(notebook_result_name))
    nbformat.write(nb, notebook_result_name)
