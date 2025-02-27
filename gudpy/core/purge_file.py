import os
import sys
import subprocess

from PySide6.QtCore import QProcess
from core.enums import Instruments
from core.utils import resolve, spacify, numifyBool
from core import config

SUFFIX = ".exe" if os.name == "nt" else ""


class PurgeFile():
    """
    Class to represent a PurgeFile.

    ...

    Attributes
    ----------
    gudrunFile : GudrunFile
        Parent GudrunFile that we are creating the PurgeFile from.
    excludeSampleAndCan : bool
        Exclude sample and container data files?
    instrumentName : str
        Name of the instrument.
    inputFileDir : str
        Input file directory for Gudrun.
    dataFileDir : str
        Data file directory.
    dataFileType : str
        Type of files stored in dataFileDir.
    detCalibFile : str
        Filename used for detector calibration.
    groupsFile : str
        Name of detector groups file to read from.
    spectrumNumbers : int[]
        Number of spectra of incident beam monitor.
    channelNumbers : tuple(int, int)
        First and last channel numbers to check for spikes.
        0 0 signals to use all channels.
    acceptanceFactor : int
        Acceptance factor for spike analysis.
    standardDeviation : tuple(int, int)
         Stores the number of std deviations allowed above and below
         the mean ratio and the range of std's allowed around the mean
         standard deviation.
    ignoreBad : bool
        Ignore any existing bad spectrum files (spec.bad, spec.dat)?
    normalisationPeriodNo : int
        Period number for normalisation data files.
    normalisationPeriodNoBg : int
        Period number for normalisation background data files.
    normalisationDataFiles : str
        String representation of all normalisation data files,
        and their period numbers.
    normalisationBackgroundDataFiles : str
        String representation of all background normalisation data files,
        and their period numbers.
    sampleBackgroundDataFiles : str
        String representation of all sample background data files,
        and their period numbers.
    sampleDataFiles : str
        String representation of all sample data files,
        and their period numbers.
    containerDataFiles : str
        String representation of all containers data files,
        and their period numbers.
    Methods
    -------
    collectGudrunFileAttributes()
        Collects the attributes needed for the purge file.
    write_out()
        Writes out the string representation of the PurgeFile to purge_det.dat
    purge()
        Writes out the file, and then calls purge_det on that file.
    """
    def __init__(
            self,
            gudrunFile
    ):
        """
        Constructs all the necessary attributes for the PurgeFile object.

        Parameters
        ----------
        gudrunFile : GudrunFile
            Parent GudrunFile that we are creating the PurgeFile from.
        """
        self.gudrunFile = gudrunFile
        self.excludeSampleAndCan = True
        self.standardDeviation = (10, 10)
        self.ignoreBad = True

        self.collectGudrunFileAttributes()

    def write_out(self, path=""):
        """
        Writes out the string representation of the PurgeFile to
        purge_det.dat.

        Parameters
        ----------
        None
        Returns
        -------
        None
        """
        # Write out the string representation of the PurgeFile
        # To purge_det.dat.
        if not path:
            f = open("purge_det.dat", "w", encoding="utf-8")
            f.write(str(self))
        else:
            f = open(path, "w", encoding="utf-8")
            f.write(str(self))
        f.close()

    def collectGudrunFileAttributes(self):
        """
        Collects the attributes needed for the purge file, from the
        GudrunFile object.

        Parameters
        ----------
        None
        Returns
        -------
        None
        """

        # Extract relevant attributes from the GudrunFile object.
        self.instrumentName = self.gudrunFile.instrument.name
        self.inputFileDir = self.gudrunFile.instrument.GudrunInputFileDir
        self.dataFileDir = self.gudrunFile.instrument.dataFileDir
        self.detCalibFile = (
            os.path.join(
                self.gudrunFile.instrument.GudrunStartFolder,
                self.gudrunFile.instrument.detectorCalibrationFileName
            )
        )
        self.groupsFile = (
            os.path.join(
                self.gudrunFile.instrument.GudrunStartFolder,
                self.gudrunFile.instrument.groupFileName
            )
        )
        self.spectrumNumbers = (
            self.gudrunFile.instrument.spectrumNumbersForIncidentBeamMonitor
        )
        self.channelNumbers = (
            self.gudrunFile.instrument.channelNosSpikeAnalysis
        )
        self.acceptanceFactor = (
            self.gudrunFile.instrument.spikeAnalysisAcceptanceFactor
        )
        self.normalisationPeriodNo = (
            self.gudrunFile.normalisation.periodNumber
        )
        self.normalisationPeriodNoBg = (
            self.gudrunFile.normalisation.periodNumberBg
        )

        self.normalisationDataFiles = (
            self.gudrunFile.normalisation.dataFiles.dataFiles,
            self.gudrunFile.normalisation.periodNumber
        )
        self.normalisationBackgroundDataFiles = (
            self.gudrunFile.normalisation.dataFilesBg.dataFiles,
            self.gudrunFile.normalisation.periodNumberBg
        )

        # Iterate through sample backgrounds, samples and containers
        # data files, building a list of data files and period numbers.
        # only append samples and their containers, if
        # the sample is set to run.
        self.sampleBackgroundDataFiles = [
            (sb.dataFiles.dataFiles, sb.periodNumber)
            for sb in self.gudrunFile.sampleBackgrounds
        ]
        self.sampleDataFiles = [
            (s.dataFiles.dataFiles, s.periodNumber)
            for sb in self.gudrunFile.sampleBackgrounds
            for s in sb.samples if s.runThisSample
        ]
        self.containerDataFiles = [
            (c.dataFiles.dataFiles, c.periodNumber)
            for sb in self.gudrunFile.sampleBackgrounds
            for s in sb.samples if s.runThisSample
            for c in s.containers
        ]

    def __str__(self):
        """
        Returns the string representation of the PurgeFile object.

        Parameters
        ----------
        None

        Returns
        -------
        string : str
            String representation of PurgeFile.
        """
        HEADER = f"'  '  '          '  '{os.path.sep}'\n\n"
        TAB = "          "

        # Collect data files as strings of the format:
        # {name} {period number}
        # do this for normalisation, normalisation background,
        # sample background, sample and container data files.
        # insert eight space 'tab' after each period number,
        # for consistency with original Gudrun code.

        TAB = "          "
        self.normalisationDataFilesString = ""
        self.normalisationBackgroundDataFilesString = ""

        # Iterate through normalisation and normalisation background
        # data files, appending their string representation with
        # period number to the relevant string.
        for dataFile in self.normalisationDataFiles[0]:
            self.normalisationDataFilesString += (
                f"{dataFile}  {str(self.normalisationPeriodNo)}{TAB}\n"
            )
        for dataFile in self.normalisationBackgroundDataFiles[0]:
            self.normalisationBackgroundDataFilesString += (
                f"{dataFile}  {str(self.normalisationPeriodNoBg)}{TAB}\n"

            )
        self.sampleBackgroundDataFilesString = ""
        self.sampleDataFilesString = ""
        self.containerDataFilesString = ""

        # Iterate through sample background
        # data files, appending their string representation with
        # period number to the relevant string.
        for dataFiles, periodNumber in self.sampleBackgroundDataFiles:
            for dataFile in dataFiles:
                self.sampleBackgroundDataFilesString += (
                    f"{dataFile}  {str(periodNumber)}{TAB}\n"
                )
        # Iterate through sample data files,
        # appending their string representation with
        # period number to the relevant string.
        for dataFiles, periodNumber in self.sampleDataFiles:
            for dataFile in dataFiles:
                self.sampleDataFilesString += (
                    f"{dataFile}  {str(periodNumber)}{TAB}\n"
                )

        # Iterate through container data files,
        # appending their string representation with
        # period number to the relevant string.
        for dataFiles, periodNumber in self.containerDataFiles:
            for dataFile in dataFiles:
                self.containerDataFilesString += (
                    f"{dataFile}  {str(periodNumber)}{TAB}\n"
                )

        dataFileLines = (
            f'{self.normalisationDataFilesString}'
            f'{self.normalisationBackgroundDataFilesString}'
            f'{self.sampleBackgroundDataFilesString}'
            f'{self.sampleDataFilesString}'
            f'{self.containerDataFilesString}'
            if not self.excludeSampleAndCan
            else
            f'{self.normalisationDataFilesString}'
            f'{self.normalisationBackgroundDataFilesString}'
            f'{self.sampleBackgroundDataFilesString}'
        )
        return (
            f'{HEADER}'
            f'{Instruments(self.instrumentName.value).name}{TAB}'
            f'Instrument name\n'
            f'{self.inputFileDir}{TAB}'
            f'Gudrun input file directory:\n'
            f'{self.dataFileDir}{TAB}'
            f'Data file directory\n'
            f'{self.detCalibFile}{TAB}'
            f'Detector calibration file name\n'
            f'{self.groupsFile}{TAB}'
            f'Groups file name\n'
            f'{spacify(self.spectrumNumbers)}{TAB}'
            f'Spectrum number(s) for incident beam monitor\n'
            f'{spacify(self.channelNumbers, num_spaces=2)}{TAB}'
            f'Channel numbers for spike analysis\n'
            f'{self.acceptanceFactor}{TAB}'
            f'Spike analysis acceptance factor\n'
            f'{spacify(self.standardDeviation, num_spaces=2)}{TAB}'
            f'Specify the number of standard deviations allowed'
            f' above and below the mean ratio.'
            f' Specify the range of std\'s allowed'
            f' around the mean standard deviation.\n'
            f'{numifyBool(self.ignoreBad)}{TAB}'
            f'Ignore any existing bad spectrum and spike files'
            f' (spec.bad, spike.dat)?\n'
            f'{dataFileLines}'
        )

    def purge(
        self,
        standardDeviation=(10, 10),
        ignoreBad=True,
        excludeSampleAndCan=True,
        headless=True
    ):
        """
        Write out the current state of the PurgeFile, then
        purge detectors by calling purge_det on that file.

        Parameters
        ----------
        standardDeviation: tuple(int, int), optional
            Number of std deviations allowed above and below
            the mean ratio and the range of std's allowed around the mean
            standard deviation. Default is (10, 10)
        ignoreBad : bool, optional
            Ignore any existing bad spectrum files (spec.bad, spec.dat)?
            Default is True.
        excludeSampleAndCan : bool, optional
            Exclude sample and container data files?
        headless : bool
            Should headless mode be used?
        Returns
        -------
        subprocess.CompletedProcess
            The result of calling purge_det using subprocess.run.
            Can access stdout/stderr from this.
        """
        self.standardDeviation = standardDeviation
        self.ignoreBad = ignoreBad
        self.excludeSampleAndCan = excludeSampleAndCan
        if headless:
            try:
                cwd = os.getcwd()
                purge_det = resolve("bin", f"purge_det{SUFFIX}")
                os.chdir(self.gudrunFile.instrument.GudrunInputFileDir)
                self.write_out()
                result = subprocess.run(
                    [purge_det, "purge_det.dat"],
                    capture_output=True,
                    text=True
                )
                os.chdir(cwd)
            except FileNotFoundError:
                return False
            return result
        else:
            if hasattr(sys, '_MEIPASS'):
                purge_det = os.path.join(sys._MEIPASS, f"purge_det{SUFFIX}")
            else:
                purge_det = resolve(
                    os.path.join(
                        config.__rootdir__, "bin"
                    ), f"purge_det{SUFFIX}"
                )
            if not os.path.exists(purge_det):
                return FileNotFoundError()
            proc = QProcess()
            proc.setProgram(purge_det)
            proc.setArguments([])
            return (
                proc,
                self.write_out,
                [
                    os.path.join(
                        self.gudrunFile.instrument.GudrunInputFileDir,
                        "purge_det.dat"
                    )
                ]
            )
