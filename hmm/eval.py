def get_common_segment_nums(seg_tags0, seg_tags1):

    len0 = len(seg_tags0)
    len1 = len(seg_tags1)
    if (len0 < len1):
        leng = len0
    else:
        leng = len1
        
    common = 0
    for i in xrange(leng):
        a = seg_tags0[i]
        b = seg_tags1[i]
        if (a=="|" and b=="|"):
            common += 1
    return common

def get_segment_nums(seg_tags):

    num = 0
    for tag in seg_tags:
        if (tag == "|"):
            num += 1
    return num
            
def segment(tags):

    seg_tags = []
    count = 0
    for tag in tags:
        count += 1
        seg_tags.append(tag)
        if (count == tag):
            seg_tags.append("|")
            count = 0
    return seg_tags
        
def getFScore(tagss0, tagss1):

    seg_tagss0 = [segment(tags0) for tags0 in tagss0]
    seg_tagss1 = [segment(tags1) for tags1 in tagss1]
    common = 0
    num1 = 0
    num2 = 0
    for (seg_tags0, seg_tags1) in zip(seg_tagss0, seg_tagss1):
        common += get_common_segment_nums(seg_tags0, seg_tags1)
    for seg_tags0 in seg_tagss0:
        num1 += get_segment_nums(seg_tags0)
    for seg_tags1 in seg_tagss1:
        num2 += get_segment_nums(seg_tags1)

    precision = float(common) / float(num2)
    recall = float(common) / float(num1)

    return 2.0 * precision * recall / (precision + recall)
