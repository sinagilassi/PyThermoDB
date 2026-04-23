# import libs
from rich import print
from pyThermoDB.references.reference_maker import ReferenceMaker

# ! reference
from examples.databooks.reference import REFERENCE_CONTENT


# SECTION: create reference content
# NOTE: ideal-gas-heat-capacity
# COLUMNS: [No.,Name,Formula,State,a0,a1,a2,a3,a4,R,Eq]
# VALUES:
# - [1,'carbon dioxide','CO2','g',3.259,1.356,1.502,-2.374,1.056,8.314,1]
CO2_dt_1 = [1, 'carbon dioxide', 'CO2', 'g',
            3.259, 1.356, 1.502, -2.374, 1.056, 8.314, 1]
CO_dt_1 = [2, 'carbon monoxide', 'CO', 'g',
           3.912, -3.913, 1.182, -1.302, 0.515, 8.314, 1]


# NOTE: general-data
# COLUMNS: [No.,Name,Formula,State,Molecular-Weight,Critical-Temperature,Critical-Pressure,Critical-Molar-Volume,Critical-Compressibility-Factor,Acentric-Factor,Enthalpy-of-Formation,Gibbs-Energy-of-Formation]
# VALUES:
# - [1,'carbon dioxide','CO2','g',44.01,304.21,7.383,0.094,0.274,0.2236,-393.5,-394.4]
CO2_dt_2 = [1, 'carbon dioxide', 'CO2', 'g', 44.01,
            304.21, 7.383, 0.094, 0.274, 0.2236, -393.5, -394.4]
CO_dt_2 = [2, 'carbon monoxide', 'CO', 'g', 28.01,
           132.92, 3.499, 0.0944, 0.299, 0.0482, -110.5, -137.2]

# NOTE: create reference maker
reference_maker = ReferenceMaker(REFERENCE_CONTENT)

# reference content
print("[bold green]Reference content:[/bold green]")
print(reference_maker.reference)


# NOTE: update values
res_ = reference_maker.update_table_values(
    databook_name='CUSTOM-REF-1',
    table_name='ideal-gas-heat-capacity',
    new_values=[CO2_dt_1, CO_dt_1]
)
print("[bold green]Updated reference content:[/bold green]")
print(res_)

res_ = reference_maker.update_table_values(
    databook_name='CUSTOM-REF-1',
    table_name='general-data',
    new_values=[CO2_dt_2, CO_dt_2]
)
print("[bold green]Updated reference content:[/bold green]")
print(res_)

# ! check reference
reference_updated = reference_maker.reference
print("[bold green]Updated reference content:[/bold green]")
print(reference_updated)
