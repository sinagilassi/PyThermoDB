# import libs
from rich import print
from pyThermoDB.references import load_reference_from_str
# ! reference
from examples.databooks.reference_original import REFERENCE_CONTENT

# SECTION: load reference content
reference = load_reference_from_str(REFERENCE_CONTENT)
print("[bold green]Reference content:[/bold green]")
print(reference)
