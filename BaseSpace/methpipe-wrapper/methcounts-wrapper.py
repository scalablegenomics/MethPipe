import os
import subprocess
import json
import sys

class DockerApp:
    def __init__(self):
        appconf = "/data/input/AppSession.json" if len(sys.argv) == 1 \
          else sys.argv[1]
        jf = json.load(open(appconf))
        properties = jf["Properties"]["Items"]
        properties = dict(zip([p["Name"] for p in properties], properties))

        self.methcounts_app = "/home/methpipe/methpipe/bin/methcounts"
        self.bsrate_app = "/home/methpipe/methpipe/bin/bsrate"
        
        self.InAppResultID = properties["Input.AppResults"]["Items"][0]["Id"]
        self.genomefile = properties["Input.genome-file"]["Content"]["Path"]
        self.genomefile = "/data/input/appresults/" + self.InAppResultID \
          + "/" + self.genomefile

        self.mappedReadFile = properties["Input.mr-file"]["Content"]["Path"]
        self.mappedReadFile = "/data/input/appresults/" + self.InAppResultID \
          + "/" + self.mappedReadFile

        self.maxReadLen = properties["Input.max-read-length"]["Content"]
        self.maxMismatches = properties["Input.max-mismatch"]["Content"]

        self.nonCpG = "-non" if "Input.non-CpG" in properties else ""
        self.verbose = "-verbose"
        
        self.outProjID = properties["Input.project-id"]["Content"]["Id"]

        self.methfile = self.mappedReadFile.replace(".mr", ".meth")
        self.methfile = self.methfile.replace( \
            "/data/input/appresults/" + self.InAppResultID + "/", \
            "/data/output/appresults/" + self.outProjID + "/meth/")          

        self.methstatsfile = self.methfile.replace(".meth", ".methstats")
        self.bsratefile = self.methfile.replace(".meth", ".bsrate")

    def run(self):
        # run methcounts program
        command_list = [self.methcounts_app, self.mappedReadFile, \
                        "-output", self.methfile, \
                        "-output_stat", self.methstatsfile, \
                        "-chrom", self.genomefile, \
                        "-max_length", self.maxReadLen, \
                        "-max", self.maxMismatches, self.verbose]
        if not self.nonCpG: command_list.append(self.nonCpG)
        print "\t".join(command_list)
        outdir = os.path.dirname(self.methfile)
        if not os.path.exists(outdir):
            os.makedirs(outdir)
        rcode = subprocess.call( command_list )
        if rcode != 0 : raise Exception("methcounts process exited abnormally")

        # run bsrate program
        command_list = [self.bsrate_app, self.mappedReadFile, \
                        "-output", self.bsratefile, \
                        "-chrom", self.genomefile, \
                        "-max", self.maxMismatches, self.verbose]
        print "\t".join(command_list)
        rcode = subprocess.call( command_list )
        if rcode != 0 : raise Exception("bsrate process exited abnormally")
            
            
#the entry point
if __name__ == "__main__" :
    DockerApp().run()


    
