import sys
import numpy as np

input_filename = sys.argv[1]
percentile_filename = sys.argv[2]
output_filename = sys.argv[3]

with open(percentile_filename) as f:
    p = np.int(f.read())

def parse_line(line):
    """parse a line from an itcont file
    and return the important fields as a dictiory"""
    fields = line.split('|')
    r_dict = {}
    ######
    r_dict['CMTE_ID'] = fields[0]
    r_dict['NAME'] = fields[7]
    r_dict['ZIP_CODE'] = fields[10][:5]
    r_dict['YEAR'] = int(fields[13][-4:])
    r_dict['TRANSACTION_AMT'] = fields[14]
    r_dict['OTHER_ID'] = fields[15]
    return r_dict

def check_parse(transaction):
    """determine if a parsed transaction line transaction
    should be processed. Returns true if Ok"""
    ok = True
    ok = ok & (len(transaction['OTHER_ID'])==0)
    return ok

with open(output_filename, 'wt') as outfile:
    with open(input_filename) as f: 
        doners = {}
        recipients = {}
        for line in f:
            trans = parse_line(line)
            if check_parse(trans):
                doner_item = {'YEAR':trans['YEAR']}
                recipient_item = {'TRANS':[int(trans['TRANSACTION_AMT'])],
                                  'YEAR':trans['YEAR']}
                d = doners.setdefault((trans['NAME'],trans['ZIP_CODE']),doner_item)
                if not d is doner_item:
                    #we have a repeat doner!
                    #was the last donation line from this doner from an earlier year?
                    #otherwise if there was a donation with a more recent year 
                    #ignore the current line
                    if d['YEAR'] <= doner_item['YEAR']:
                        #if so then update the record for this year
                        r = recipients.setdefault((trans['CMTE_ID'],
                                                    trans['ZIP_CODE'],
                                                    doner_item['YEAR']),
                                                    recipient_item)
                        if not r is recipient_item:
                            r['TRANS'].append(np.int(trans['TRANSACTION_AMT']))
                        #now update the doners dictionary so that the doner year
                        #is current.
                        doners[(trans['NAME'],trans['ZIP_CODE'])] = doner_item
                        #output
                        outfile.write('%s|%s|%s|%s|%s|%s\n'%(trans['CMTE_ID'],
                                      trans['ZIP_CODE'],
                                      trans['YEAR'],
                                      int(round(np.percentile(r['TRANS'],p,
                                                  interpolation='lower'))),
                                      np.sum(r['TRANS']), len(r['TRANS'])))
