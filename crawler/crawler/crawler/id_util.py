import datetime
import random
import time


def generate_pv_gid():
    # table: pv, pic_video
    return generate_gid('PV')


def generate_post_gid():
    return generate_gid('PT')


def generate_uid():
    """
    generate user id
    :return:
    """
    return generate_gid()


def generate_merch_item_gid():
    return generate_gid('MI')


def generate_hashtag_gid():
    return generate_gid('HT')


def generate_media_file_gid():
    return generate_gid('MF')


def generate_post_monitor_gid():
    return generate_gid('PM')


def generate_influencer_gid():
    return generate_gid('IF')


def generate_gid(prefix):
    # TODO check prefix
    utcnow = datetime.datetime.utcnow()
    gid = '{}{}{}{}{}{}{}{}{}'.format(prefix,
                                      utcnow.year,
                                      '{0:02d}'.format(utcnow.month),
                                      '{0:02d}'.format(utcnow.day),
                                      '{0:02d}'.format(utcnow.hour),
                                      '{0:02d}'.format(utcnow.minute),
                                      '{0:02d}'.format(utcnow.second),
                                      '{0:06d}'.format(utcnow.microsecond),
                                      '{0:08d}'.format(random.randint(0, 99999999))
                                      )
    return gid


def generate_gid2(next_seq_id=None):
    """
    TODO add test
    Each of our IDs consists of:

    41 bits for time in milliseconds (gives us 41 years of IDs with a custom epoch)
        41*365*24*3600*1000 = 1,200 B
        2^41 = 2,199 B

    # 13 bits that represent the logical shard ID

    10 bits that represent an auto-incrementing sequence, modulus 1024.
        This means we can generate 1024 IDs, per shard, per millisecond.

    :param next_seq_id:
    :return:
    """

    ts = int(time.time() * 10000000)
    gid = ts << 10 & 0x7FFFFFFFFFFFFFFF
    if not next_seq_id:
        next_seq_id = random.randint(0, 65535)
    gid |= (next_seq_id % 1024)
    return gid


def generate_file_name():
    """
    for each user, Just use time in milliseconds as file name for now
    :return:
    """
    ts = int(time.time())
    return str(ts)


if __name__ == "__main__":
    """
    For testing
    """
    id_set = set()
    for i in range(100000000):
        id2 = generate_influencer_gid()
        print("======== {}".format(id2))
        id2 = generate_pv_gid()
        if id2 in id_set:
            print ("====*****==== {}".format(id2))
        else:
            id_set.add(id2)
            # print(id2)
