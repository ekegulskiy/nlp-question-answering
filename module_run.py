import argparse
import sys
#from config import Config

parser = argparse.ArgumentParser()
"""
parser.add_argument('--kg', dest='kg_instance', required=True, type=check_kg, help="Specify kg_instance, choices are 'gkg' for Google KG or 'dkg' for Diffbot KG")
parser.add_argument('--factoid-pipeline', dest='factoid_pipeline', action='store_true', help="Use factoid pipeline in KGQA2")
parser.add_argument('--enable-stats', dest='enable_stats', action='store_true', help="Enable stats collection")
"""
parser.add_argument('--module', dest='module', required=True, help="Module to run (QPM, FMQFM, DSOEM, FAESM)")
parser.add_argument('--question', dest='question', required=True, help="any question you want to ask")

args = parser.parse_args()
#Config.collect_stats = args.enable_stats

#from test_utils import *

from QPM import QPM

print("")

if args.module.upper() == "QPM":
    qpm = QPM(args.question)
else:
    print("Unrecognized module")