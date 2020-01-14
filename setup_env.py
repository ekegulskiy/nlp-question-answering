import os
import urllib.request
import zipfile
from git import Repo
import progressbar

STANFORD_POS_TAGGER = "https://nlp.stanford.edu/software/stanford-postagger-2018-10-16.zip"
STANFORD_NER_TAGGER = "https://nlp.stanford.edu/software/stanford-ner-2018-10-16.zip"

# This function is taken from https://stackoverflow.com/questions/37748105/how-to-use-progressbar-module-with-urlretrieve
class MyProgressBar():
    def __init__(self):
        self.pbar = None

    def __call__(self, block_num, block_size, total_size):
        if not self.pbar:
            self.pbar=progressbar.ProgressBar(maxval=total_size)
            self.pbar.start()

        downloaded = block_num * block_size
        if downloaded < total_size:
            self.pbar.update(downloaded)
        else:
            self.pbar.finish()


def download_and_unzip(zip_url, unzip_dir):
    if not os.path.exists(unzip_dir):
        target_zip_file = os.path.basename(zip_url)
        print("Downloading {}".format(zip_url))
        urllib.request.urlretrieve("{}".format(zip_url), target_zip_file, MyProgressBar())
        print("Unzipping {}".format(target_zip_file))
        zip_ref = zipfile.ZipFile(target_zip_file, 'r')
        zip_ref.extractall(unzip_dir)
        zip_ref.close()
        os.remove(target_zip_file)
    else:
        print("{} already exists, skipping download of {}".format(unzip_dir, zip_url))


#if not os.path.exists(BERT_DIR):
#    print("Cloning BERT repository from ".format(BERT_GIT_URL))
#    Repo.clone_from(BERT_GIT_URL, BERT_DIR)

download_and_unzip(STANFORD_POS_TAGGER, "")
download_and_unzip(STANFORD_NER_TAGGER, "")

#print("Downloading {}".format(ADRMINE_DATA_ADR_LEXICON_NAME))
#urllib.request.urlretrieve("{}".format(ADRMINE_DATA_ADR_LEXICON_URL), ADRMINE_DATA_ADR_LEXICON_NAME)
