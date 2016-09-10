import commands
import json
import os
import pickle
import sys

import upgradeScripts

class Updates():
    def __init__(self, local_path, runGithubSync = False, runBashScripts = False):
        self.local_path = local_path
        self.network_path = os.path.dirname(os.path.realpath(__file__))
        self.version_pickle_path = "%s/%s" % (self.network_path, "version.pickle")
        self.default_version_number = 0.0
        print self.local_path, self.network_path, self.version_pickle_path

    def run_bash_command(self, cmd):
        status, output = commands.getstatusoutput(cmd)
        return (status, output)
        # log any errors

    def run_github_sync(self):
        cmd = "cd %s && git pull -q --all -p" % (self.local_path)
        return self.run_bash_command(cmd)

    def make_version_pickle(self):
        if not os.path.isfile(self.version_pickle_path):
            pfile = open(self.version_pickle_path, "wb")
            pickle.dump(self.default_version_number, pfile)
            return True
        return False

    def read_version_pickle(self):
        if not os.path.isfile(self.version_pickle_path):
            self.make_version_pickle()
            return self.default_version_number
        return pickle.load(open(self.version_pickle_path, "r"))

    def write_version_pickle(self, version):
        if not os.path.isfile(self.version_pickle_path):
            self.make_version_pickle()
            return self.default_version_number
        pickle.dump(float(version),open(self.version_pickle_path, "wb"))

    def reset_version_pickle(self):
        if not os.path.isfile(self.version_pickle_path):
            self.make_version_pickle()
        pfile = open(self.version_pickle_path, "wb")
        pickle.dump(self.default_version_number, pfile)

    def run_uprade_scripts(self):
        import upgradeScripts
        v_l =  upgradeScripts.scripts.keys()
        v_l.sort(key=float)
        msg = []
        versionFromPickle = self.read_version_pickle()
        for version in v_l:
            if float(version) >= versionFromPickle:
                for script in upgradeScripts.scripts[version]:
                    status, output = self.run_bash_command(script)
                    msg.append((version, status, output))
        return msg

def init(local_path, runGithubSync = False, runBashScripts = False):
    updates = Updates(local_path, runGithubSync, runBashScripts)
    #   updates.reset_version_pickle()
    ghStatus = ""
    bsStatus = []
    if runGithubSync:
        ghStatus = updates.run_github_sync()
    if runBashScripts:
        bhStatus = updates.run_uprade_scripts()
    return (updates, ghStatus, bsStatus)
