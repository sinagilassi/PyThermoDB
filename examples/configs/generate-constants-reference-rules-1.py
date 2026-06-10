# import libs
import os
from rich import print
from typing import Dict
# import pyThermoDB
from pyThermoDB.references import ReferenceChecker
# ! reference
from examples.configs.reference_2 import REFERENCE_CONTENT

# NOTE: current file path
parent_path = os.path.dirname(os.path.abspath(__file__))
print(parent_path)

# ==========================================
# SECTION: create ReferenceChecker instance
# ==========================================
ReferenceChecker_ = ReferenceChecker(REFERENCE_CONTENT)

# ==========================================
# SECTION: Check Constants Availability
# ==========================================

# ==========================================
# SECTION: Constants Reference Config
# ==========================================

# ==========================================
# SECTION: Constants Reference Configs
# ==========================================

# ==========================================
# SECTION: Constants Reference Rules
# ==========================================
