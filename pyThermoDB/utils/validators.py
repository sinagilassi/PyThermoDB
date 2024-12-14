# VALIDATOR
# used to check reference data format
# =====================================

# import packages/modules


class ValidatorRef:
    def __init__(self):
        pass

    @staticmethod
    def matrix_data_checker(data):
        """Check matrix data format defined in a reference file (yml)"""
        try:
            # keys
            group_keys = ['COLUMNS', 'SYMBOL', 'UNIT', 'CONVERSION']
        except Exception as e:
            raise Exception(
                f"Checking matrix data failed {e}, check yml reference file.")
