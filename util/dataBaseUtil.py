import textUtil

def prepare_for_database(source):
    sentences = textUtil.sent_splitter(source)
    sentences = [textUtil.prepare_decode(s) for s in sentences]
    return sentences
