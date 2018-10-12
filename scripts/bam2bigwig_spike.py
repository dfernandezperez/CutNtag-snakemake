import subprocess
import pysam
import os
from argparse import ArgumentParser

######################
## ARGUMENT PARSING ##
######################
parser = ArgumentParser(description='Bam to bigwig for spike-in samples')
parser.add_argument('-c', '--case', help='case sample bam file', required=True)
parser.add_argument('-s', '--spike', help='spike-in bam file', required=True)
parser.add_argument('-r', '--reference', help='reference file (input) bam file', required=True)
parser.add_argument('-b', '--bigwig', help='name for the output bigwig file', required=True)
parser.add_argument('-x', '--chrSizes', help='Chromosome sizes file', required=True)
parser.add_argument('-p', '--threads', help='Number of threads to use', required=True)
parser.add_argument('-e', '--extReads', help='Number of threads to use', required=True)

options = parser.parse_args()

case = options.case
spike = options.spike
reference = options.reference
chr_sizes = options.chrSizes
threads = options.threads
e_reads = options.extReads
bw = options.bigwig
bdg = case + ".bdg"


##############################
## Avoid warning from pysam ##
##############################
def touch_file(file):
	command = "touch " + file
	subprocess.call(command.split())

# Avoid the warning from pysam that tells that the bam file is more recent than the index file (due to snakemake behaviour)
touch_file(spike + ".bai")
touch_file(case + ".bai")

####################
## Read bam files ##
####################
r = pysam.AlignmentFile(reference, "rb")
dm = pysam.AlignmentFile(spike, "rb")
c = pysam.AlignmentFile(case, "rb")

################################################################
## Calculate normalization factors: (1/mapped reads)*1million ##
################################################################
reference_norm = str( (1.0/float(r.mapped))*1000000 )
dm_norm = str( (1.0/float(dm.mapped))*1000000 )
case_norm = str( (1.0/float(c.mapped))*1000000 )

sampleNorm2spikeNorm = str( (1.0/float(case_norm))*float(dm_norm) )

#############################
## Bash commands to launch ##
#############################
bamCompare = "bamCompare -b1 " + case + " -b2 " + reference + " -o " + bw + " --operation subtract --scaleFactors " + case_norm + ":" + reference_norm + " -p " + threads + " --extendReads " + e_reads

wiggleTools = "wiggletools write_bg " + bdg + " scale " + sampleNorm2spikeNorm + " " + bw

bdg2bw = "bedGraphToBigWig " + bdg + " " + chr_sizes + " " + bw

subprocess.call(bamCompare.split())
subprocess.call(wiggleTools.split())
subprocess.call(bdg2bw.split())

# Cleaning bedgraph file
os.remove(bdg)

