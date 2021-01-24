import argparse
import sys
#from config import Config

parser = argparse.ArgumentParser()
"""
parser.add_argument('--factoid-pipeline', dest='factoid_pipeline', action='store_true', help="Use factoid pipeline in KGQA2")
parser.add_argument('--enable-stats', dest='enable_stats', action='store_true', help="Enable stats collection")
"""
parser.add_argument('--module', dest='module', required=True, help="Module to run (1, 2, 3, 4)")
parser.add_argument('--question', dest='question', required=True, help="any question you want to ask")
parser.add_argument('--ds', dest='ds', required=False, help="Specify data source, choices are 'gkg' for Google KG or 'dkg' for Diffbot KG")
parser.add_argument('--ds-api-key', dest='ds_api_key', required=False, help="Specify API key/token for the given data source")

args = parser.parse_args()
#Config.collect_stats = args.enable_stats

#from test_utils import *

from QPM import QPM
from FMQFM import FMQFM
from DSOEM import DSOEM
from FAESM import FAESM

if args.module.upper() == "1":
    # instantiate first module of the pipeline: QPM
    qpm = QPM(args.question)

elif args.module.upper() == "2":
    # instantiate 2 pipeline modules: QPM and QMQFM, and connect them together
    qpm = QPM(args.question)
    fmqfm = FMQFM(qpm)

elif args.module.upper() == "3":
    # instantiate 3 pipeline modules: QPM, QMQFM, and DSOEM and connect them together
    if args.ds is None:
        raise Exception("data source required for running DSOEM module (see help)")
    if args.ds_api_key is None:
        raise Exception("data source api key/token required for running DSOEM module (see help)")

    qpm = QPM(args.question)
    fmqfm = FMQFM(qpm)
    dsoem = DSOEM(fmqfm, args.ds, args.ds_api_key, qpm)

elif args.module.upper() == "4":
    # instantiate 4 pipeline modules: QPM, QMQFM, DSOEM and FAESM and connect them together
    if args.ds is None:
        raise Exception("data source required for running DSOEM module (see help)")
    if args.ds_api_key is None:
        raise Exception("data source api key/token required for running DSOEM module (see help)")

    qpm = QPM(args.question)
    fmqfm = FMQFM(qpm)
    dsoem = DSOEM(fmqfm, args.ds, args.ds_api_key, qpm)
    faesm = FAESM(dsoem)
    answers = faesm.top_answers()
else:
    print("Unrecognized module")