"""Synthetic dashboard contracts; local benchmark files are not test prerequisites."""
import json
from pathlib import Path
import pytest

from ear_rag.dashboard_data import run_question, load_benchmarks
from ear_rag.data.musique import read_musique
from ear_rag.config.loader import load_config, get_config_path
from test_musique_ingestion import record, write


def test_live_uses_real_pipeline_and_only_safe_runtime_inputs(tmp_path, monkeypatch):
    import ear_rag.dashboard_data as service
    original = service._pipeline
    inputs = []
    def capture(documents, config):
        inputs.append(json.dumps([d.metadata for d in documents]))
        return original(documents, config)
    monkeypatch.setattr(service, '_pipeline', capture)
    dataset=read_musique(write(tmp_path,[record()]))
    raw=(tmp_path/'native.jsonl').read_bytes()
    result=run_question(dataset,'q1',load_config(get_config_path()))
    assert result['question']==record()['question']
    assert result['initial']['assessment']['overall_score']>=0
    assert result['calls']>=1 and result['final_status'] in ('ANSWERABLE','ABSTAIN')
    assert result['initial']['evidence'][0]['paragraph_idx'] in (0,1)
    assert (tmp_path/'native.jsonl').read_bytes()==raw
    assert 'SECRET' not in json.dumps(result)
    second=run_question(dataset,'q1',load_config(get_config_path()))
    assert len(inputs)==2 and all('is_supporting' not in value and 'SECRET' not in value for value in inputs)
    assert result['initial']['evidence']==second['initial']['evidence']
    assert result['final_status']==second['final_status']


def test_saved_results_read_counts_and_nulls_without_executing_pipeline(tmp_path,monkeypatch):
    import ear_rag.dashboard_data as service
    def forbidden(*a,**k): raise AssertionError('benchmark reader executed pipeline')
    monkeypatch.setattr(service,'_pipeline',forbidden)
    directory=tmp_path/'hotpot'/'fixed_local_lexical_no_recovery'; directory.mkdir(parents=True)
    artifact={'counts':{'requested':5,'evaluated':4,'failed':0,'excluded':1},
        'terminal':{'hit_at_5':{'mean':.75},'supporting_document_recall_at_5':{'mean':None}},
        'work':{'retrieval_calls':{'total':4}}}
    (directory/'aggregate.json').write_text(json.dumps(artifact))
    rows,errors=load_benchmarks(tmp_path,{'HotpotQA development':('hotpot','aggregate')})
    assert len(errors)==5  # Missing conditions remain visible, never silently dropped.
    assert rows['HotpotQA development'][0]['Recall@5'] is None
    assert rows['HotpotQA development'][0]['Excluded']==1
    assert (directory/'aggregate.json').read_text()==json.dumps(artifact)


def test_missing_results_are_explicit(tmp_path):
    rows,errors=load_benchmarks(tmp_path,{'Missing':('absent','aggregate')})
    assert rows['Missing']==[] and errors


def test_ui_runs_synthetic_controller_and_hides_stale_result(tmp_path, monkeypatch):
    pytest.importorskip('streamlit')  # Optional UI dependency, not a core test prerequisite.
    from streamlit.testing.v1 import AppTest
    import ear_rag.dashboard_data as service
    monkeypatch.setattr(service, 'DATASET', write(tmp_path, [record(), record('q2')]))
    monkeypatch.setattr(service, 'load_benchmarks', lambda *a: ({'Synthetic': []}, []))
    app = AppTest.from_file(str(Path(service.__file__).with_name('dashboard.py'))).run()
    assert not app.exception
    assert [tab.label for tab in app.tabs] == ['Live Query Demo', 'Benchmark Results']
    app.button[0].click().run()
    assert not app.exception and int(app.metric[2].value) >= 1
    assert any('CAS > tau:' in item.value for item in app.code)
    assert any('uncertain' in item.value and 'insufficient' in item.value for item in app.markdown)
    score_tables = [item.value for item in app.dataframe if 'Difference' in item.value.columns]
    assert len(score_tables) == 1 and len(score_tables[0]) == 5
    app.selectbox[0].select('q2').run()
    assert not app.exception and not app.metric


def test_trained_artifact_and_malformed_report(tmp_path):
    directory=tmp_path/'trained'; directory.mkdir()
    (directory/'results.json').write_text(json.dumps({'results': {'trained_router': {
        'requested':3,'evaluated':2,'failed_ids':['failed'], 'hit_at_5':.5,
        'paragraph_recall_at_5':.25,'retrieval_calls':2}}}))
    tables,errors=load_benchmarks(tmp_path,{'Trained':('trained','trained')})
    assert not errors
    assert tables['Trained'][0]['Failed']==1 and tables['Trained'][0]['Excluded']==0
    (directory/'results.json').write_text('{bad')
    tables,errors=load_benchmarks(tmp_path,{'Trained':('trained','trained')})
    assert tables['Trained']==[] and len(errors)==1


def test_candidate_display_preserves_runtime_arithmetic_and_strict_boundary():
    from ear_rag.dashboard_data import candidate_rows
    result = {'initial': {'assessment': {'overall_score': .89}},
              'configuration': load_config(),
              'decision': {'parameters': {}, 'metadata': {'cas_threshold': 1.0, 'recover': False,
                  'candidate_evaluations': [
                      {'backend': 'vector_flat', 'eligible': True, 'suitability': 1.0,
                       'reason': 'missing query tokens', 'evidence_deficiency': .11,
                       'raw_incremental_cost': .11, 'incremental_cost': .11, 'cas': 1.0,
                       'estimated_work': {'retrieval_calls': 1, 'retrieved_chunks': 5, 'latency_ms': 10}},
                      {'backend': 'local_lexical', 'eligible': False, 'suitability': 0.0,
                       'reason': 'backend already attempted'}]}}}
    before = json.dumps(result)
    rows = candidate_rows(result)
    assert rows[0]['CAS'] == 1 and rows[0]['Threshold passed'] is False
    assert rows[0]['Suitability (0/1)'] == 1 and rows[0]['Nominal latency ms'] == 10
    assert '(1 - 0.89)' in rows[0]['Arithmetic'] and '/ 0.11' in rows[0]['Arithmetic']
    assert rows[1]['CAS'] is None and rows[1]['Threshold passed'] is None
    assert 'not evaluated' in rows[1]['Arithmetic']
    assert json.dumps(result) == before


def test_score_comparison_and_paragraph_sets_preserve_duplicate_rank_entries():
    from ear_rag.dashboard_data import compare_stages
    initial = {'assessment': dict(overall_score=.6,relevance=.4,coverage=.5,support=.5,consistency=1),
               'evidence': [{'paragraph_idx': i} for i in [0,2,8,19,13]]}
    recovery = {'assessment': dict(overall_score=.55,relevance=.2,coverage=.5,support=.5,consistency=1),
                'evidence': [{'paragraph_idx': i} for i in [2,4,13,12,12]]}
    rows, paragraphs = compare_stages({'initial':initial,'recovery':recovery})
    assert rows[0]['Difference'] == pytest.approx(-.05)
    assert paragraphs == {'Initial (rank order)': [0,2,8,19,13],
                          'Recovery (rank order)': [2,4,13,12,12],
                          'New in recovery': [4,12], 'Overlap': [2,13], 'Initial only': [0,8,19]}
    rows, paragraphs = compare_stages({'initial':initial,'recovery':None})
    assert all(row['Difference']==0 for row in rows)
    assert paragraphs['Recovery (rank order)'] is None
