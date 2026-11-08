import json
def dumps(d):
    """the assets' layout: a key a line; parts, shapes, coats one a line; variants one a line"""
    L = ['{']
    keys = list(d)
    for i, k in enumerate(keys):
        v = d[k]; comma = ',' if i < len(keys) - 1 else ''
        if k in ('parts', 'coats') and isinstance(v, list):
            L.append(f'  "{k}": [')
            L += ['    ' + json.dumps(x) + (',' if j < len(v) - 1 else '') for j, x in enumerate(v)]
            L.append('  ]' + comma)
        elif k == 'variants' and isinstance(v, dict):
            L.append(f'  "{k}": {{')
            ks = list(v)
            L += [f'    {json.dumps(n)}: ' + json.dumps(v[n]) + (',' if j < len(ks) - 1 else '') for j, n in enumerate(ks)]
            L.append('  }' + comma)
        elif k == 'sculpt' and isinstance(v, dict):
            L.append('  "sculpt": {')
            sk = list(v)
            for j, kk in enumerate(sk):
                c2 = ',' if j < len(sk) - 1 else ''
                if kk == 'shape':
                    L.append('    "shape": [')
                    L += ['      ' + json.dumps(x) + (',' if m < len(v[kk]) - 1 else '') for m, x in enumerate(v[kk])]
                    L.append('    ]' + c2)
                else:
                    L.append(f'    "{kk}": ' + json.dumps(v[kk]) + c2)
            L.append('  }' + comma)
        else:
            L.append(f'  "{k}": ' + json.dumps(v) + comma)
    L.append('}')
    return '\n'.join(L) + '\n'
