def prepare_notebook(notebook_path, notebook_result_path, colab=False):
    if colab:
        import requests
        import urllib.parse
        import google.colab
        import os
        
        mount_dir = '/content/drive'

        google.colab.drive.mount(mount_dir)

        def locate_nb(set_singular=True):
            found_files = []
            paths = [ mount_dir + '/MyDrive/' + notebook_path, '/content/drive/MyDrive/']
            colab_ip = "172.28.0.12"
            colab_port = 9000
            nb_address = f"http://{colab_ip}:{colab_port}/api/sessions"
            response = requests.get(nb_address).json()
            name = urllib.parse.unquote(response[0]['name'])

            dir_candidates = []

            for path in paths:
                for dirpath, subdirs, files in os.walk(path):
                    for file in files:
                        if file == name:
                            found_files.append(os.path.join(dirpath, file))

            found_files = list(set(found_files))

            if len(found_files) == 1:
                nb_dir = os.path.dirname(found_files[0])
                dir_candidates.append(nb_dir)
                if set_singular:
                    print('Singular location found, setting directory')
                    os.chdir(dir_candidates[0])
            elif not found_files:
                print('Notebook file name not found.')
            elif len(found_files) > 1:
                print('Multiple matches found, returning list of possible locations.')
                dir_candidates = [os.path.dirname(f) for f in found_files]

            return dir_candidates, name

        locations, name = locate_nb()
        notebook_path = locations[0] + '/' + name
        
    
    import nbformat
    nb = nbformat.read(notebook_path, as_version=nbformat.NO_CONVERT)

    for i, cell in enumerate(nb.cells):
        if "## TEACHER" in cell.source or "##TEACHER" in cell.source:
            nb.cells.pop(i)
            continue
        
        if "## KEEPOUTPUT" not in cell.source or "##KEEPOUTPUT" not in cell.source:
            nb.cells[i].outputs = []

    nbformat.write(nb, notebook_result_path)
    print("Student Notebook saved on ".format(locations[0] if locations else notebook_result_path))