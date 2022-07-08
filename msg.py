import polib
po = polib.pofile('msg.po')
msg = {}
for entry in po:
    msg[entry.msgid] = entry.msgstr


def read_msg(index):
    if index not in msg.keys():
        return None
    else:
        return msg[index]
