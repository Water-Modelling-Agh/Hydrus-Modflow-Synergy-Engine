
import os

import version_contants


def verify_dir_exists_or_create(path: str):
    if not os.path.isdir(path):
        print('Directory ' + path + ' does not exist, creating...')
        os.system('mkdir ' + path)


class AppUtils:

    def __init__(self):
        self.allowed_types = ["ZIP", "RAR", "7Z"]
        self.project_root = version_contants.PROJECT_ROOT
        self.workspace_dir = os.path.join(self.project_root, 'workspace')
        self.modflow_dir = os.path.join(self.workspace_dir, 'modflow')
        self.hydrus_dir = os.path.join(self.workspace_dir, 'hydrus')
        self.active_project = None
        self.all_projects = []
        self.loaded_hydrus_models = []  # an array of strings, the names of the loaded hydrus models
        self.loaded_modflow_models = []
        self.nam_file_name = ""
        self.recharge_masks = []
        self.loaded_shapes = {}
        self.modflow_rows = 0
        self.modflow_cols = 0
        self.error_flag = False

    def setup(self) -> None:
        self.loaded_hydrus_models = []
        self.loaded_modflow_models = []
        self.nam_file_name = ""
        self.recharge_masks = []
        self.loaded_shapes = {}
        self.modflow_rows = 0
        self.modflow_cols = 0
        verify_dir_exists_or_create(self.workspace_dir)
        verify_dir_exists_or_create(self.modflow_dir)
        verify_dir_exists_or_create(self.hydrus_dir)
        self.error_flag = False

    def get_error_flag(self) -> bool:
        error_flag = self.error_flag
        self.error_flag = False
        return error_flag

    def type_allowed(self, filename: str) -> bool:
        """
        @param filename: Path to the file whose extension needs to be checked
        @return: True if file has valid extension, False otherwise
        """

        # check if there even is an extension
        if '.' not in filename:
            return False

        # check if it's allowed
        extension = filename.rsplit('.', 1)[1]
        return extension.upper() in self.allowed_types
