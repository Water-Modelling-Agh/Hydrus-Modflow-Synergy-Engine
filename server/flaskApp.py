from flask import Flask, render_template, request, redirect
from zipfile import ZipFile

import os
import json

from AppUtils import AppUtils

util = AppUtils()
util.setup()
app = Flask("App")


# ------------------- EXAMPLES -------------------

all_posts = [
    {
        'title': "post 1",
        'content': "this is content",
        'author': "Marek Gajecki"
    },
    {
        'title': "post 2",
        'content': "this is also content"
    }
]


# template rendering
@app.route('/')
def home():
    return render_template('index.html')


# parameter passing and method declaration - ONLY GET is allowed by default
@app.route('/home/<string:name>', methods=['GET'])
def hello(name):
    return 'sup ' + name


# template functionality showcase
@app.route('/posts')
def posts():
    return render_template('posts.html', posts=all_posts)


# ------------------- END EXAMPLES -------------------


# ------------------- ROUTES -------------------

@app.route('/upload-modflow', methods=['GET', 'POST'])
def upload_modflow():
    if request.method == 'POST' and request.files:
        return upload_modflow_handler(request)
    else:
        return render_template('uploadModflow.html')


@app.route('/upload-hydrus', methods=['GET', 'POST'])
def upload_hydrus():
    if request.method == 'POST' and request.files:
        return upload_hydrus_handler(request)
    else:
        return render_template('uploadHydrus.html', model_names=util.loaded_hydrus_models)


@app.route('/define-shape/<hydrus_model_index>', methods=['GET', 'POST'])
def define_shapes(hydrus_model_index):

    hydrus_model_index = int(hydrus_model_index)

    if request.method == 'POST':

        # if not yet done, initialize the shape arrays list to the amount of models
        if len(util.loaded_shapes) < len(util.loaded_hydrus_models):
            util.loaded_shapes = [None for _ in range(len(util.loaded_hydrus_models))]

        # read the array from the request and store it
        shape_array = request.get_json(force=True)
        util.loaded_shapes[hydrus_model_index] = shape_array

        return json.dumps({'status': 'OK'})

    else:

        # check if we still have models to go, if not, redirect to next section
        if hydrus_model_index >= len(util.loaded_hydrus_models):
            # TODO - change this to actual content once actual content exists
            print(util.loaded_shapes)
            return render_template('index.html')

        else:
            return render_template(
                'defineShapes.html',
                rowAmount=util.modflow_rows,
                colAmount=util.modflow_cols,
                rows=[str(x) for x in range(util.modflow_rows)],
                cols=[str(x) for x in range(util.modflow_cols)],
                modelIndex=hydrus_model_index,
                modelName=util.loaded_hydrus_models[hydrus_model_index]
            )

# ------------------- END ROUTES -------------------


# ------------------- HANDLERS -------------------

def upload_modflow_handler(req):
    project = req.files['archive-input']  # matches HTML input name

    if util.type_allowed(project.filename):

        # save, unzip, remove archive
        archive_path = os.path.join(util.workspace_dir, 'modflow', project.filename)
        project.save(archive_path)
        with ZipFile(archive_path, 'r') as archive:
            archive.extractall(os.path.join(util.workspace_dir, 'modflow'))
        os.remove(archive_path)

        print("Project uploaded successfully")
        return redirect(req.root_url + 'upload-hydrus')

    else:
        print("Invalid archive format, must be one of: ", end='')
        print(util.allowed_types)
        return redirect(req.url)


def upload_hydrus_handler(req):
    project = req.files['archive-input']  # matches HTML input name

    if util.type_allowed(project.filename):

        # save, unzip, remove archive
        archive_path = os.path.join(util.workspace_dir, 'hydrus', project.filename)
        project.save(archive_path)
        with ZipFile(archive_path, 'r') as archive:

            # get the project name and remember it
            project_name = project.filename.split('.')[0]
            util.loaded_hydrus_models.append(project_name)

            # create a dedicated catalogue and load the project into it
            os.system('mkdir ' + os.path.join(util.workspace_dir, 'hydrus', project_name))
            archive.extractall(os.path.join(util.workspace_dir, 'hydrus', project_name))

        os.remove(archive_path)

        print("Project uploaded successfully")
        return redirect(req.root_url + 'upload-hydrus')

    else:
        print("Invalid archive format, must be one of: ", end='')
        print(util.allowed_types)
        return redirect(req.url)

# ------------------- END HANDLERS -------------------
