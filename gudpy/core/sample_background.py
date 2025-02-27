from core.data_files import DataFiles


class SampleBackground:
    """
    Class to represent a SampleBackground.

    ...

    Attributes
    ----------
    periodNumber : int
        Period number for data files.
    dataFiles : DataFiles
        DataFiles object storing data files belonging to the container.
    samples : Sample[]
        List of Sample objects against the SampleBackground.
    Methods
    -------
    """
    def __init__(self):
        """
        Constructs all the necessary attributes for the
        SampleBackground object.

        Parameters
        ----------
        None
        """
        self.periodNumber = 1
        self.dataFiles = DataFiles([], "SAMPLE BACKGROUND")
        self.samples = []
        self.writeAllSamples = True

        self.yamlignore = {
            "writeAllSamples",
            "yamlignore"
        }

    def __str__(self):
        """
        Returns the string representation of the SampleBackground object.

        Parameters
        ----------
        None

        Returns
        -------
        string : str
            String representation of SampleBackground.
        """
        TAB = "          "
        CONV_SAMPLES = [
            str(c.convertToSample())
            for s in self.samples
            for c in s.containers
            if c.runAsSample
        ]
        if self.writeAllSamples:
            samples = [str(x) for x in self.samples]
        else:
            samples = [str(x) for x in self.samples if x.runThisSample]
        SAMPLES = "\n".join([*samples, *CONV_SAMPLES])
        self.writeAllSamples = True

        dataFilesLine = (
            f'{str(self.dataFiles)}\n'
            if len(self.dataFiles) > 0
            else
            ''
        )

        return (
            f'SAMPLE BACKGROUND{TAB}{{\n\n'
            f'{len(self.dataFiles)}  {self.periodNumber}{TAB}'
            f'Number of  files and period number\n'
            f'{dataFilesLine}\n'
            f'}}\n'
            f'{SAMPLES}'

        )
