
"""Nicer config class."""

import os, os.path, ConfigParser, socket

__all__ = ['Config']

class Config(object):
    """Bit improved ConfigParser.

    Additional features:
     - Remembers section.
     - Acceps defaults in get() functions.
     - List value support.
    """
    def __init__(self, main_section, filename, sane_config = 1, user_defs = {}):
        """Initialize Config and read from file.

        @param sane_config:  chooses between ConfigParser/SafeConfigParser.
        """
        # use config file name as default job_name
        if filename:
            job_name = os.path.splitext(os.path.basename(filename))[0]
        else:
            job_name = main_section

        # initialize defaults, make them usable in config file
        self.defs = {
            'job_name': job_name,
            'service_name': main_section,
            'host_name': socket.gethostname(),
        }
        self.defs.update(user_defs)

        self.main_section = main_section
        self.filename = filename
        self.sane_config = sane_config
        if sane_config:
            self.cf = ConfigParser.SafeConfigParser()
        else:
            self.cf = ConfigParser.ConfigParser()

        if filename is None:
            self.cf.add_section(main_section)
        elif not os.path.isfile(filename):
            raise Exception('Config file not found: '+filename)

        self.reload()

    def reload(self):
        """Re-reads config file."""
        if self.filename:
            self.cf.read(self.filename)
        if not self.cf.has_section(self.main_section):
            raise Exception("Wrong config file, no section '%s'" % self.main_section)
        for k, v in self.defs.items():
            if not self.cf.has_option(self.main_section, k):
                self.cf.set(self.main_section, k, v)

    def get(self, key, default=None):
        """Reads string value, if not set then default."""
        try:
            return self.cf.get(self.main_section, key)
        except ConfigParser.NoOptionError:
            if default == None:
                raise Exception("Config value not set: " + key)
            return default

    def getint(self, key, default=None):
        """Reads int value, if not set then default."""
        try:
            return self.cf.getint(self.main_section, key)
        except ConfigParser.NoOptionError:
            if default == None:
                raise Exception("Config value not set: " + key)
            return default

    def getboolean(self, key, default=None):
        """Reads boolean value, if not set then default."""
        try:
            return self.cf.getboolean(self.main_section, key)
        except ConfigParser.NoOptionError:
            if default == None:
                raise Exception("Config value not set: " + key)
            return default

    def getfloat(self, key, default=None):
        """Reads float value, if not set then default."""
        try:
            return self.cf.getfloat(self.main_section, key)
        except ConfigParser.NoOptionError:
            if default == None:
                raise Exception("Config value not set: " + key)
            return default

    def getlist(self, key, default=None):
        """Reads comma-separated list from key."""
        try:
            s = self.cf.get(self.main_section, key).strip()
            res = []
            if not s:
                return res
            for v in s.split(","):
                res.append(v.strip())
            return res
        except ConfigParser.NoOptionError:
            if default == None:
                raise Exception("Config value not set: " + key)
            return default

    def getdict(self, key, default=None):
        """Reads key-value dict from parameter.
        
        Key and value are separated with ':'.  If missing,
        key iself is taken as value.
        """
        try:
            s = self.cf.get(self.main_section, key).strip()
            res = {}
            if not s:
                return res
            for kv in s.split(","):
                tmp = kv.split(':', 1)
                if len(tmp) > 1:
                    k = tmp[0].strip()
                    v = tmp[1].strip()
                else:
                    k = kv.strip()
                    v = k
                res[k] = v
            return res
        except ConfigParser.NoOptionError:
            if default == None:
                raise Exception("Config value not set: " + key)
            return default

    def getfile(self, key, default=None):
        """Reads filename from config.
        
        In addition to reading string value, expands ~ to user directory.
        """
        fn = self.get(key, default)
        if fn == "" or fn == "-":
            return fn
        # simulate that the cwd is script location
        #path = os.path.dirname(sys.argv[0])
        #  seems bad idea, cwd should be cwd

        fn = os.path.expanduser(fn)

        return fn

    def get_wildcard(self, key, values=[], default=None):
        """Reads a wildcard property from conf and returns its string value, if not set then default."""
        
        orig_key = key
        keys = [key]
        
        for wild in values:
            key = key.replace('*', wild, 1)
            keys.append(key)
        keys.reverse()

        for key in keys:
            try:
                return self.cf.get(self.main_section, key)
            except ConfigParser.NoOptionError:
                pass

        if default == None:
            raise Exception("Config value not set: " + orig_key)
        return default
    
    def sections(self):
        """Returns list of sections in config file, excluding DEFAULT."""
        return self.cf.sections()

    def clone(self, main_section):
        """Return new Config() instance with new main section on same config file."""
        return Config(main_section, self.filename, self.sane_config)


    def options(self):
        """Return list of options in main section."""
        return self.cf.options(self.main_section)

    def has_option(self, opt):
        """Checks if option exists in main section."""
        return self.cf.has_option(self.main_section, opt)

