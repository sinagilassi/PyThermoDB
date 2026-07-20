# import libs
from pyThermoDB import (
    MixtureThermoDB,
    build_mixture_thermodb_from_reference,
)
from pythermodb_settings.models import Component
from rich import print

# SECTION: reference content
# NOTE:
# A ternary mixture is encoded as binary pair rows. For three components,
# the unfiltered multi-component build expects all three binary pairs:
# methanol|ethanol, methanol|butyl-methyl-ether, and
# ethanol|butyl-methyl-ether. Each pair has two rows.
REFERENCE_CONTENT = """
REFERENCES:
    CUSTOM-REF-TERNARY:
      DATABOOK-ID: 1
      TABLES:
        NRTL Non-randomness parameters-ternary:
          TABLE-ID: 1
          DESCRIPTION:
            This table provides NRTL matrix parameters for a ternary mixture through binary pair rows.
          MATRIX-SYMBOL:
            - a constant: a
            - b constant: b
            - c constant: c
            - non-randomness parameter: alpha
          STRUCTURE:
            COLUMNS: [No.,Mixture,Name,Formula,State,a_i_1,a_i_2,b_i_1,b_i_2,c_i_1,c_i_2,alpha_i_1,alpha_i_2]
            SYMBOL: [None,None,None,None,None,a_i_1,a_i_2,b_i_1,b_i_2,c_i_1,c_i_2,alpha_i_1,alpha_i_2]
            UNIT: [None,None,None,None,None,1,1,1,1,1,1,1,1]
          VALUES:
            - [1,methanol|ethanol,methanol,CH3OH,l,0,0.300492719,0,1.564200272,0,35.05450323,0,4.481683583]
            - [2,methanol|ethanol,ethanol,C2H5OH,l,0.380229054,0,-20.63243601,0,0.059982839,0,4.481683583,0]
            - [1,methanol|butyl-methyl-ether,methanol,CH3OH,l,0,0.1201,0,2.25,0,18.4,0,0.680715]
            - [2,methanol|butyl-methyl-ether,butyl-methyl-ether,C5H12O,l,0.2152,0,-8.75,0,0.041,0,0.680715,0]
            - [1,ethanol|butyl-methyl-ether,ethanol,C2H5OH,l,0,0.1803,0,3.268,0,22.6,0,0.680715]
            - [2,ethanol|butyl-methyl-ether,butyl-methyl-ether,C5H12O,l,0.2457,0,-12.48,0,0.052,0,0.680715,0]
"""

# SECTION: components
methanol = Component(
    name='methanol',
    formula='CH3OH',
    state='l'
)

ethanol = Component(
    name='ethanol',
    formula='C2H5OH',
    state='l'
)

butyl_methyl_ether = Component(
    name='butyl-methyl-ether',
    formula='C5H12O',
    state='l'
)

# ! multi-component mixture
multi_component_mixture = [methanol, ethanol, butyl_methyl_ether]

# SECTION: build all binary pairs in the ternary mixture
thermodb_ternary: MixtureThermoDB | None = build_mixture_thermodb_from_reference(
    components=multi_component_mixture,
    reference_content=REFERENCE_CONTENT,
    component_key='Name-State',
    mixture_key='Name',
)
print(f"thermodb_ternary: {type(thermodb_ternary)}")

if thermodb_ternary is not None:
    print(f"thermodb_ternary checks: {thermodb_ternary.thermodb.check()}")

# SECTION: build only selected binary pairs from the same ternary component list
thermodb_ternary_selected: MixtureThermoDB | None = build_mixture_thermodb_from_reference(
    components=multi_component_mixture,
    reference_content=REFERENCE_CONTENT,
    component_key='Name-State',
    mixture_key='Name',
    mixture_names=[
        "methanol | ethanol",
        "ethanol | butyl-methyl-ether",
    ],
)
print(f"thermodb_ternary_selected: {type(thermodb_ternary_selected)}")

if thermodb_ternary_selected is not None:
    print(
        f"thermodb_ternary_selected checks: {thermodb_ternary_selected.thermodb.check()}"
    )
