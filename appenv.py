import os
import tempfile
import logging

class cls_appenv(object):
    def __init__(self):
        self.tmpdir = tempfile.gettempdir()
        self.homedir = os.path.expanduser('~')
        self.workdir = os.path.join(self.homedir, '.ppdict')
        if not os.path.exists(self.workdir):
            try:
                os.makedirs(self.workdir)
            except IOError:
                pass
        self.logfile = os.path.join(self.workdir, 'ppdict.log')
        self.prefsfile = os.path.join(self.workdir, 'prefs.ini')
        self.logger = None
        self.installdir = None
        try:
            from  config import installdir
            self.installdir = installdir
        except ImportError:
            self.installdir = os.getcwd()
        self.datadir = os.path.join(self.installdir, 'share', 'data')
        self.dictdir = os.path.join(self.installdir, 'share', 'dicts')
        self.uidir = os.path.join(self.installdir, 'share', 'ui')
        self.iconsdir = os.path.join(self.installdir, 'share', 'icons')
        self.simpledb = os.path.join(self.datadir, 'simpledb.gz')
        self.prefixdb = os.path.join(self.datadir, 'prefixdb.gz')
        self.valcabuarydb = os.path.join(self.datadir, 'valcabuarydb.gz')
        self.correctordb = os.path.join(self.datadir, 'correctordb.gz')
        self.correctorres = os.path.join(self.datadir, 'big.txt.gz')

    def get_tmp_dir(self):
        return self.tmpdir

    def get_home_dir(self):
        return self.homedir

    def get_work_dir(self):
        return self.workdir

    def get_logger(self):
        if not self.logger:
            logfmt = '%(asctime)s.%(msecs)03d [%(process)d] %(levelname)-4s %(message)s'
            logdatefmt = '%Y-%m-%d %H:%M:%S'
            logging.basicConfig(filename=self.logfile, level=logging.DEBUG, format=logfmt, datefmt=logdatefmt)
            self.logger = logging.getLogger()

        return self.logger
    
    def get_prefs_file(self):
        return self.prefsfile

    def get_log_file(self):
        return self.logfile

    def get_data_dir(self):
        return self.datadir

    def get_ui_dir(self):
        return self.uidir

    def get_dict_dir(self):
        return self.dictdir

    def get_icons_dir(self):
        return self.iconsdir

    def get_simpledb(self):
        return self.simpledb

    def get_prefixdb(self):
        return self.prefixdb

    def get_correctordb(self):
        return self.correctordb

    def get_valcabuarydb(self):
        return self.valcabuarydb

    def get_corrector_res(self):
        return self.correctorres

env = cls_appenv()
log = env.get_logger()
