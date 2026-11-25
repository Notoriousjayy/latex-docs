#!/usr/bin/env python3
"""Dependency-free structural checks. Not a complete JSON Schema or semantic audit."""
import json,sys
from pathlib import Path

def validate(data):
    errors=[]; ids=set(); indexes={}
    for k in ('stakeholders','concerns','views','elements','relations','evidence','correspondences'):
        items=data.get(k)
        if not isinstance(items,list): errors.append(f'{k}: missing or not list'); items=[]
        indexes[k]={}
        for item in items:
            if not isinstance(item,dict): errors.append(f'{k}: invalid record'); continue
            id=item.get('id')
            if not isinstance(id,str) or not id: errors.append(f'{k}: missing ID'); continue
            if id in ids: errors.append(f'duplicate ID {id}')
            ids.add(id); indexes[k][id]=item
    def ref(val,kind,label):
        if not isinstance(val,str) or val not in indexes[kind]: errors.append(f'{label}: unresolved {kind} {val!r}')
    if not isinstance(data.get('baseline'),str) or not data['baseline'].strip(): errors.append('missing baseline')
    if data.get('status') not in ('observed','proposed','mixed'): errors.append('invalid document status')
    for id,c in indexes['concerns'].items():
        ref(c.get('stakeholder'),'stakeholders',id)
        views=c.get('views',[])
        if not isinstance(views,list): errors.append(f'{id}: views not a list'); views=[]
        if c.get('priority')=='high' and (not views or not c.get('disposition')): errors.append(f'{id}: high concern lacks view/disposition')
        for v in views: ref(v,'views',id)
    for kind in ('elements','relations'):
        for id,x in indexes[kind].items():
            if x.get('status') not in ('observed','inferred','proposed','unknown'): errors.append(f'{id}: invalid status')
            ev=x.get('evidence',[])
            if not isinstance(ev,list): errors.append(f'{id}: evidence not list'); ev=[]
            if x.get('status')=='observed' and not ev: errors.append(f'{id}: observed claim lacks evidence')
            if x.get('status') in ('inferred','unknown') and not x.get('note'): errors.append(f'{id}: missing explanation')
            for e in ev: ref(e,'evidence',id)
    for kind in ('relations','correspondences'):
        for id,x in indexes[kind].items():
            ref(x.get('source'),'elements',id); ref(x.get('target'),'elements',id)
            if not x.get('type'): errors.append(f'{id}: missing relation type')
    for id,e in indexes['evidence'].items():
        a,b=e.get('start_line'),e.get('end_line')
        if not all(e.get(k) for k in ('revision','path','observation')) or type(a) is not int or type(b) is not int or a<1 or b<a: errors.append(f'{id}: incomplete evidence range')
    return errors

def main():
    if len(sys.argv)!=2: print('usage: validate.py MANIFEST.json',file=sys.stderr); return 2
    try:
        data=json.loads(Path(sys.argv[1]).read_text())
        if not isinstance(data,dict): raise ValueError('manifest must be an object')
        errors=validate(data)
    except (OSError,ValueError,TypeError) as e: print(f'ERROR: {e}',file=sys.stderr); return 2
    if errors:
        print('FAIL:\n'+'\n'.join(errors));return 1
    print('PASS: structural checks only; semantic and stakeholder review still required');return 0
if __name__=='__main__':sys.exit(main())
