# import packages/modules
import os
import yaml


class CustomRef:
    '''
    Manage new custom references
    '''

    def __init__(self, ref):
        self.ref = ref
        self.yml_files: list[str] = []
        self.csv_files: list[str] = []
        self.yml_paths: list[str] = []
        self.csv_paths: list[str] = []
        # symbols
        self.symbols_files: list[str] = []
        self.symbols_paths: list[str] = []

    def init_ref(self) -> bool:
        '''
        Update reference through updating yml

        Notes
        ----------
        yml_files : list
            yml files 
        csv_files : list
            csv files

        Returns
        -------
        bool
            True if reference is updated, False otherwise
        '''
        try:
            # extract data
            # reference
            yml_files = self.ref.get('yml') or self.ref.get('reference') or []
            # tables
            csv_files = self.ref.get('csv') or self.ref.get('tables') or []
            # symbols (optional)
            symbol_files = self.ref.get('symbols') or []

            # check files exist
            if len(yml_files) == 0:
                raise Exception("No yml files to update.")
            if len(csv_files) == 0:
                raise Exception("No csv files to update.")

            # check file path
            for yml_file in yml_files:
                if not os.path.exists(yml_file):
                    raise Exception(f"{yml_file} does not exist.")
                else:
                    # get path
                    self.yml_paths.append(os.path.abspath(yml_file))
            for csv_file in csv_files:
                if not os.path.exists(csv_file):
                    raise Exception(f"{csv_file} does not exist.")
                else:
                    # get path
                    self.csv_paths.append(os.path.abspath(csv_file))

            # update vars
            self.yml_files = yml_files
            self.csv_files = csv_files

            # check
            if len(symbol_files) > 0:
                # symbols
                for symbol_file in symbol_files:
                    if not os.path.exists(symbol_file):
                        raise Exception(f"{symbol_file} does not exist.")
                    else:
                        # get path
                        self.symbols_paths.append(os.path.abspath(symbol_file))

                # update vars
                self.symbols_files = symbol_files

            return True
        except Exception as e:
            raise Exception(f"updating reference failed! {e}")

    def load_ref(self) -> dict:
        '''
        Load reference

        Returns
        -------
        ref : dict
            reference
        '''
        try:
            # data
            data = {}
            # loop through the rest of the files
            for i in range(0, len(self.yml_files)):
                with open(self.yml_files[i], 'r') as f:
                    # load data
                    temp_data = yaml.load(f, Loader=yaml.FullLoader)
                    # check
                    if temp_data is None:
                        raise Exception("No data in the file number %d" % i)
                    # merge data
                    data.update(temp_data['REFERENCES'])

            # res
            return data
        except Exception as e:
            raise Exception(f"loading reference failed! {e}")

    def load_symbols(self) -> dict:
        '''
        Load symbols

        Returns
        -------
        symbols : dict
            symbols
        '''
        try:
            # data
            data = {}

            # check
            if self.symbols_files is not None:
                # loop through the rest of the files
                for i in range(0, len(self.symbols_files)):
                    with open(self.symbols_files[i], 'r') as f:
                        # load data
                        temp_data = yaml.load(f, Loader=yaml.FullLoader)
                        # check
                        if temp_data is None:
                            raise Exception(
                                "No data in the file number %d" % i)
                        # merge data
                        data.update(temp_data['SYMBOLS'])

            # res
            return data
        except Exception as e:
            raise Exception(f"loading symbols failed! {e}")
