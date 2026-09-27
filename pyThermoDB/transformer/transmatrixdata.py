# import packages/modules
# external

# internal


class TransMatrixData:
    """Transform API payloads into component-keyed matrix data mappings.

    Each input item represents one component and contains its identifying
    metadata together with an API payload. The transformer converts each
    payload into a header-keyed mapping and indexes that mapping by component
    name, optional formula, and optional state-qualified identifiers.

    Parameters
    ----------
    api_data_pack : list[dict]
        Component payloads. Each item must contain ``component_name`` and
        ``data`` and may contain ``component_formula`` and ``component_state``.
    component_delimiter : str, default='-'
        Separator used when building name-state and formula-state keys.

    Notes
    -----
    The API payload under each ``data`` item must provide aligned ``header``,
    ``records``, ``unit``, and ``symbol`` sequences. The original payload is
    retained under the ``matrix-data`` key in each transformed record.

    Methods
    -------
    trans()
        Transform and index all component matrix payloads.
    """

    __data_type = ''

    def __init__(
            self,
            api_data_pack,
            component_delimiter: str = '-'
    ):
        """Initialize a matrix-data transformer.

        Parameters
        ----------
        api_data_pack : list[dict]
            Component payloads to transform.
        component_delimiter : str, default='-'
            Separator used for compound component identifiers.

        Notes
        -----
        The delimiter is stripped before use, and the detected equation ID is
        stored on ``self.eq_id`` when an ``Eq`` header is encountered.
        """
        # NOTE: set attributes
        self.api_data_pack = api_data_pack
        self.component_delimiter = component_delimiter.strip()
        self.eq_id = None

        # NOTE: transformed data
        self.data_trans_pack = {}

    @property
    def data_type(self):
        """Return the detected type, such as ``'matrix-data'`` or ``'matrix-equations'``."""
        return self.__data_type

    @data_type.setter
    def data_type(self, value):
        """Set the detected matrix payload type."""
        self.__data_type = value

    def trans(self):
        """Transform and index all component matrix-data payloads.

        Returns
        -------
        dict
            Mapping from component identifiers to transformed header mappings.
            Each component is indexed by its name and, when supplied, its
            formula, name-state, and formula-state identifiers.

        Notes
        -----
        An ``Eq`` header sets ``data_type`` to ``'matrix-equations'`` and
        stores its record in ``eq_id``. Other processed headers set the type
        to ``'matrix-data'``. The last processed header determines the final
        value when a pack mixes payload types.
        """
        self.data_trans_pack = {}

        # SECTION: looping through api_data_pack
        for i, api_component_data in enumerate(self.api_data_pack):
            # NOTE: set
            component_name = api_component_data['component_name']
            api_data = api_component_data['data']
            # optional fields
            component_formula = api_component_data.get(
                'component_formula', None
            )
            component_state = api_component_data.get('component_state', None)

            # data trans
            data_trans = {}
            # looping through api_data
            for x, y, z, w in zip(
                api_data['header'], api_data['records'], api_data['unit'], api_data['symbol']
            ):
                # check eq exists
                if x == "Eq":
                    self.eq_id = y
                    # set data type
                    self.__data_type = 'matrix-equations'
                else:
                    self.__data_type = 'matrix-data'

                # set values
                data_trans[str(x)] = {
                    "value": y, "unit": z, "symbol": w
                }

            # NOTE: data table
            data_trans['matrix-data'] = api_data

            # SECTION: set name
            self.data_trans_pack[str(component_name)] = data_trans
            # >> name-state if available
            # set state
            if component_state is not None:
                key = f"{component_name}{self.component_delimiter}{component_state}"
                self.data_trans_pack[str(key)] = data_trans

            # SECTION: set formula and state if available
            if component_formula is not None:
                # >> save
                self.data_trans_pack[str(component_formula)] = data_trans

                # >> formula-state if available
                if component_state is not None:
                    key = f"{component_formula}{self.component_delimiter}{component_state}"
                    self.data_trans_pack[str(key)] = data_trans

        # res
        return self.data_trans_pack
