# import packages/modules
# external
import pandas as pd
# internal


class TransData:
    """Transform API component records into the package's lookup format.

    The transformer consumes an API payload containing parallel ``header``,
    ``records``, ``unit``, and ``symbol`` sequences. It produces a mapping in
    which each header is associated with its value, unit, and symbol, while
    retaining the original payload under the ``data`` key.

    Parameters
    ----------
    api_data : dict
        API payload containing ``header``, ``records``, ``unit``, and
        ``symbol`` entries.

    Notes
    -----
    The data type is set to ``'equation'`` when the payload contains an
    ``Eq`` header; otherwise each processed record sets it to ``'data'``.
    The transformation expects the four payload sequences to be aligned.

    Methods
    -------
    trans()
        Transform the API payload into a header-keyed dictionary.
    view(value=False)
        Print the API payload as a DataFrame and optionally return it.
    """

    __data_type = ''

    def __init__(self, api_data):
        """Initialize a transformer with an API payload.

        Parameters
        ----------
        api_data : dict
            API data to transform. The payload is retained unchanged in
            ``self.api_data`` until :meth:`trans` is called.
        """
        self.api_data = api_data
        self.data_trans = {}

    @property
    def data_type(self):
        """Return the detected payload type, such as ``'data'`` or ``'equation'``."""
        return self.__data_type

    @data_type.setter
    def data_type(self, value):
        """Set the detected payload type."""
        self.__data_type = value

    def trans(self):
        """Transform the API payload into a header-keyed dictionary.

        Returns
        -------
        dict
            Mapping of each header to ``value``, ``unit``, and ``symbol``
            fields, plus the original API payload under ``'data'``.

        Notes
        -----
        If a header is ``'Eq'``, its record is stored in ``self.eq_id`` and
        the detected type becomes ``'equation'``. Other processed records set
        the detected type to ``'data'``.
        """
        self.data_trans = {}

        # loop through the data including header, records, unit, symbol
        for x, y, z, w in zip(self.api_data['header'], self.api_data['records'], self.api_data['unit'], self.api_data['symbol']):
            # check eq exists
            if x == "Eq":
                self.eq_id = y
                # set data type
                self.__data_type = 'equation'
            else:
                self.__data_type = 'data'

            # set values
            self.data_trans[str(x)] = {"value": y, "unit": z, "symbol": w}

        # data table
        self.data_trans['data'] = self.api_data
        return self.data_trans

    def view(self, value=False):
        """Print the API payload as a pandas DataFrame.

        Parameters
        ----------
        value : bool, default=False
            Return the DataFrame after printing it when true.

        Returns
        -------
        pandas.DataFrame or None
            The payload DataFrame when ``value`` is true; otherwise ``None``.
        """
        df = pd.DataFrame(self.api_data)
        print(df)
        # check
        if value:
            return df
        else:
            return None
