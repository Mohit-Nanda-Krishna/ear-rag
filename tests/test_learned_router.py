"""Synthetic trainable router contracts; no benchmark/network prerequisites."""
from copy import deepcopy
import json

import pytest

from ear_rag.core.models import Query
from ear_rag.routing.initial import STRATEGIES
from ear_rag.routing.query_analysis import FEATURE_NAMES, LightweightQueryAnalyzer
from ear_rag.routing.learned import fit_tree, feature_values, load_router, save_artifact
from ear_rag.router_training import choose_target, validate_separation
from ear_rag.data.musique import read_musique
from test_musique_ingestion import record, write


def test_training_split_identity_and_disjointness(tmp_path):
    p=write(tmp_path,[record('train-id')])
    train=read_musique(p,source_split='train')
    assert train.source['source_split']=='train'
    assert ':train:' in train.examples[0].documents[0].doc_id
    dev_r=record('dev-id'); dev_r['question']='Different development question?'
    dev=read_musique(write(tmp_path,[dev_r]))
    assert validate_separation(train,dev)['normalized_question_overlap']==[]
    dev_r['question']=train.examples[0].question.swapcase()
    with pytest.raises(ValueError,match='overlap'):
        validate_separation(train,read_musique(write(tmp_path,[dev_r])))
    with pytest.raises(ValueError,match='split'):
        validate_separation(dev,train)


def test_labels_quality_then_actual_calls_then_action_order():
    outcomes={n:{'recall':.5,'calls':2,'status':'evaluated'} for n in STRATEGIES}
    outcomes['vector_flat']['calls']=1
    assert choose_target(outcomes)['action']=='vector_flat'
    outcomes['local_lexical']['calls']=1
    assert choose_target(outcomes)['action']=='local_lexical'
    outcomes['multihop']['recall']=1
    assert choose_target(outcomes)['action']=='multihop'
    outcomes['hybrid']['status']='failed'
    assert choose_target(outcomes)['action'] is None
    outcomes['hybrid']['status']='evaluated'
    for o in outcomes.values(): o['recall']=0
    assert choose_target(outcomes)['zero_evidence'] is True
    with pytest.raises(ValueError): choose_target({})


def test_tree_save_load_determinism_four_classes_and_no_fallback(tmp_path):
    questions=['a','ab','abc','abcd']
    features=[feature_values(q) for q in questions]
    tree=fit_tree(features,list(STRATEGIES),max_depth=3,min_leaf=1)
    assert tree==fit_tree(features,list(STRATEGIES),max_depth=3,min_leaf=1)
    artifact=save_artifact(tmp_path/'router.json',tree,{'depth':3,'min_leaf':1,'seed':0})
    router=load_router(tmp_path/'router.json',artifact)
    assert [router.select(q,STRATEGIES).selected_strategy for q in questions]==list(STRATEGIES)
    with pytest.raises(ValueError,match='unavailable'):
        router.select('abcd',['local_lexical'])
    with pytest.raises(FileExistsError): save_artifact(tmp_path/'router.json',tree,{})
    with pytest.raises(ValueError,match='checksum'): load_router(tmp_path/'router.json','bad')


@pytest.mark.parametrize('defect',['schema','feature','classes','node','nonfinite'])
def test_invalid_artifacts_fail_explicitly(tmp_path,defect):
    features=[feature_values('one')]
    save_artifact(tmp_path/'a.json',fit_tree(features,['local_lexical'],max_depth=0,min_leaf=1),{})
    a=json.loads((tmp_path/'a.json').read_text())
    if defect=='schema': a['schema_version']='wrong'
    elif defect=='feature': a['features']=['answer']
    elif defect=='classes': a['classes']=['other']
    elif defect=='node': a['tree']['counts']=[-1]*4
    else: a['tree']['counts']=[float('nan')]*4
    (tmp_path/'a.json').write_text(json.dumps(a),encoding='utf-8')
    with pytest.raises(ValueError): load_router(tmp_path/'a.json')


def test_runtime_features_ignore_all_query_metadata_and_id():
    analyzer=LightweightQueryAnalyzer()
    a=analyzer.analyze(Query('2hop_GOLD','Where is Alpha?',{'answer':'SECRET','support':999}))
    b=analyzer.analyze(Query('other','Where is Alpha?',{}))
    assert a==b and set(a)==FEATURE_NAMES
    assert feature_values('Where is Alpha?')==[float(a[k]) for k in sorted(FEATURE_NAMES)]


def test_tree_fit_is_order_independent_and_development_is_not_fitted():
    from ear_rag.router_training import select_tree
    training=[]
    for i in range(128):
        training.append({'features':feature_values('short' if i<64 else 'A much longer training question'),
                         'target':{'action':STRATEGIES[i//64]}})
    dev=[{'features':feature_values('short'),'target':{'action':'multihop'},
          'outcomes':{n:{'recall':float(n=='vector_flat'),'calls':1} for n in STRATEGIES}}]
    _,search=select_tree(training,dev)
    changed=deepcopy(dev); changed[0]['target']['action']='hybrid'
    _,other=select_tree(training,changed)
    assert [r['tree'] for r in search]==[r['tree'] for r in other]
    assert all(sum(r['tree']['counts'])==128 for r in search)
    assert [r['tree'] for r in search]==[r['tree'] for r in select_tree(list(reversed(training)),dev)[1]]


def test_label_generation_is_deterministic_and_preserves_failures(tmp_path,monkeypatch):
    import ear_rag.router_training as training
    from ear_rag.config.loader import get_config_path,load_config
    data=read_musique(write(tmp_path,[record()]),source_split='train')
    config=load_config(get_config_path())
    a=training.fixed_labels(data,config,tmp_path/'a')
    b=training.fixed_labels(data,config,tmp_path/'b')
    assert a==b
    original=training.evaluate_conditions
    def failure(*args,**kwargs):
        r=original(*args,**kwargs)
        r['fixed_vector_flat_no_recovery']['per_case'][0].update(status='failed',error={'message':'synthetic'})
        return r
    monkeypatch.setattr(training,'evaluate_conditions',failure)
    failed=training.fixed_labels(data,config,tmp_path/'failure')
    assert failed[0]['question_id']=='q1' and failed[0]['target']['action'] is None
    assert failed[0]['outcomes']['vector_flat']['error']['message']=='synthetic'


def test_learned_runtime_gold_isolation_config_and_recovery(tmp_path,monkeypatch):
    from ear_rag import condition_evaluation as runner
    from ear_rag.config.loader import get_config_path,load_config
    from ear_rag.control_evaluation import EvaluationCase
    from ear_rag.routing.learned import POLICY,make_router
    from test_musique_evidence import without_timing
    from test_condition_evaluation import spy_runtime
    r=record()
    data=read_musique(write(tmp_path,[r]))
    tree=fit_tree([feature_values(r['question'])],['vector_flat'],max_depth=0,min_leaf=1)
    model=tmp_path/'model.json'; checksum=save_artifact(model,tree,{})
    config=load_config(get_config_path())
    config['query_analysis']={'enabled':True,'policy':POLICY,'artifact_path':str(model),'artifact_sha256':checksum}
    builds,calls,assessments=spy_runtime(monkeypatch,final='insufficient')
    first=runner.evaluate_conditions(data,[EvaluationCase('q1')],config,conditions=['query_aware_no_recovery','adaptive_controller'])
    r['answer']='DIFFERENT'
    r['answer_aliases']=['PRIVATE']
    r['paragraphs'][0]['is_supporting']=False; r['paragraphs'][1]['is_supporting']=True
    r['question_decomposition']=[{'id':111,'question':'PRIVATE GOLD','answer':'PRIVATE','paragraph_support_idx':1}]
    second=runner.evaluate_conditions(read_musique(write(tmp_path,[r])),[EvaluationCase('q1')],config,
                                     conditions=['query_aware_no_recovery','adaptive_controller'])
    for name in first:
        x,y=first[name]['per_case'][0],second[name]['per_case'][0]
        assert x['status']==y['status']=='evaluated',x['error']
        assert x['initial_backend']==y['initial_backend']=='vector_flat'
        assert without_timing(x['control'])==without_timing(y['control'])
        assert x['initial']['chunks']==y['initial']['chunks']
        assert x['control']['recovery_count']==int(name=='adaptive_controller')
        assert x['control']['final_state']=='abstain'
    assert [a.calls for a in assessments]==[1,2,1,2]
    assert all(q.metadata=={} for _,_,q,_,_ in calls)
    assert builds[0][0]==builds[2][0]
    with pytest.raises(ValueError,match='requires explicit'): make_router({'enabled':True,'policy':POLICY})
    with pytest.raises(FileNotFoundError): make_router({**config['query_analysis'],'artifact_path':str(tmp_path/'missing')})
