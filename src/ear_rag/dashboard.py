"""Local supervisor UI. Launch with Streamlit; never executes benchmarks."""
import math

import pandas as pd
import streamlit as st

from ear_rag.config.loader import load_config
from ear_rag.dashboard_data import DATASET, EXAMPLE, ROOT, load_benchmarks, run_question
from ear_rag.data.musique import read_musique

st.set_page_config(page_title='EAR-RAG | Supervisor Review', page_icon='🔎', layout='wide')
st.title('EAR-RAG')
st.caption('Evidence-aware retrieval · Local supervisor review')
st.info('Development/Internal — independent final evaluation pending')
live, benchmark = st.tabs(['Live Query Demo', 'Benchmark Results'])


@st.cache_data(show_spinner='Validating local MuSiQue dataset…')
def dataset_at(path: str, modified: int, size: int):
    return read_musique(path, source_split='dev')


def show_stage(label, stage):
    assessment = stage['assessment']
    st.subheader(label)
    st.write(f"Backend: **{stage['backend']}** · ESA: **{assessment['overall_score']:.6f}** · **{assessment['decision']}**")
    st.caption(assessment['rationale'])
    st.dataframe(pd.DataFrame([{key: assessment[key] for key in ('relevance', 'coverage', 'support', 'consistency')}]), hide_index=True, width='stretch')
    with st.expander(f"Retrieved evidence — {label}"):
        for rank, item in enumerate(stage['evidence'], 1):
            st.markdown(f"**{rank}. Paragraph {item['paragraph_idx']} · {item['title']}**")
            st.caption(f"{item['chunk_id']} | retrieval score {item['score']:.6f}")
            st.text(item['text'])


with live:
    st.subheader('A real question. A visible decision trail.')
    st.write('Choose a native MuSiQue development question. Run builds a fresh controller and index over that question’s candidate paragraphs using the unchanged default configuration.')
    st.caption('The first option is the verified recovery example. No answer or supporting-paragraph labels enter runtime decisions.')
    try:
        stat = DATASET.stat()
        dataset = dataset_at(str(DATASET), stat.st_mtime_ns, stat.st_size)
        ids = [e.example_id for e in dataset.examples]
        if EXAMPLE in ids:
            ids.remove(EXAMPLE)
            ids.insert(0, EXAMPLE)
        selected = st.selectbox('Dataset question ID (type to search)', ids)
        question = dataset.example_index[selected][0].question
        st.write(question)
        st.caption(f'Source: {DATASET.name} · split: dev · {len(ids):,} validated questions')
        if st.button('Run actual controller', type='primary'):
            st.session_state.pop('live_result', None)
            try:
                with st.spinner('Retrieving evidence and assessing sufficiency…'):
                    st.session_state.live_result = run_question(dataset, selected, load_config())
            except Exception as exc:
                st.error(f'Actual run failed: {type(exc).__name__}: {exc}')
        result = st.session_state.get('live_result')
        if result and result['question_id'] == selected:
            final = result['recovery'] or result['initial']
            cols = st.columns(4)
            cols[0].metric('Final evidence status', result['final_status'])
            cols[1].metric('Final ESA', f"{final['assessment']['overall_score']:.6f}")
            cols[2].metric('Retrieval calls', result['calls'])
            cols[3].metric('Returned chunks', result['chunks'])
            st.caption(f"Measured retrieval latency: {result['retrieval_latency_ms']:.3f} ms (excludes index construction and controller time).")
            st.caption(f"Nominal work cost: initial {result['nominal_initial_cost']} + executed recovery {result['nominal_recovery_cost']}. Abstract configured proxy, not money or measured compute.")
            st.subheader('1 · Query analysis and initial selection')
            if result['routing']:
                st.write(result['routing']['reason'])
                st.caption(f"Router policy: {result['routing']['policy_version']}")
            show_stage('2 · Initial retrieval → ESA', result['initial'])
            st.caption(f"Configured ESA thresholds: sufficient ≥ {result['configuration']['evidence_assessment']['sufficient_threshold']}; uncertain ≥ {result['configuration']['evidence_assessment']['uncertain_threshold']}.")
            st.subheader('3 · Deterministic recovery decision')
            decision = result['decision']
            metadata = decision['metadata']
            st.write(decision['reason'])
            st.code('CAS = (1 − current ESA) × observed suitability / incremental nominal cost\nRecover only when best eligible CAS > tau', language=None)
            if metadata.get('candidate_evaluations'):
                st.dataframe(pd.DataFrame(metadata['candidate_evaluations']).drop(columns=['estimated_work'], errors='ignore'), hide_index=True, width='stretch')
            else:
                st.caption('Candidate CAS was not evaluated; see the actual controller reason above.')
            st.write({'selected_action': decision['action_type'], 'selected_backend': decision['parameters'].get('backend'),
                      'suitability': metadata.get('suitability'), 'CAS': metadata.get('cas'),
                      'tau': metadata.get('cas_threshold'), 'recovery_accepted': metadata.get('recover', False),
                      'recovery_executed': result['recovery'] is not None})
            if result['recovery']:
                show_stage('4 · Recovery retrieval → mandatory ESA reassessment', result['recovery'])
            else:
                st.subheader('4 · No extra retrieval')
            st.subheader(f"5 · {result['final_status']}")
            st.write('ANSWERABLE means evidence passed ESA; this application does not generate an answer. ABSTAIN means evidence remained below sufficiency.')
            if selected == EXAMPLE:
                reproduced = (result['initial']['backend'] == 'vector_flat' and result['recovery'] is not None
                              and result['recovery']['backend'] == 'local_lexical'
                              and math.isclose(result['initial']['assessment']['overall_score'], .5763514422817076)
                              and math.isclose(final['assessment']['overall_score'], .9365596936944879)
                              and result['final_status'] == 'ANSWERABLE')
                if reproduced:
                    st.success('This actual run reproduced the saved recovery example.')
                else:
                    st.warning('This actual run differs from the saved example (vector_flat ESA 0.576351 → local_lexical ESA 0.936560, ANSWERABLE). The trace above is the actual outcome.')
            with st.expander('Actual trace and unchanged run configuration'):
                st.json(result)
        st.caption('Current default policy does not provide a verified real-question recovery-rejection example. No threshold or rule is changed to manufacture one.')
    except (OSError, ValueError, KeyError) as exc:
        st.error(f'Local dataset unavailable or invalid: {type(exc).__name__}: {exc}')

with benchmark:
    st.subheader('Recorded development results')
    st.write('These tables read existing artifacts. Opening this tab never runs an experiment or trains a model.')
    tables, errors = load_benchmarks(ROOT / 'outputs')
    experiment = st.selectbox('Recorded experiment', list(tables))
    is_hotpot = experiment.startswith('HotpotQA')
    st.caption('Recall@5 unit: ' + ('supporting document (HotpotQA)' if is_hotpot else 'native supporting paragraph (MuSiQue; parent paragraphs deduplicated from first five chunks)'))
    st.caption('Hit@5: at least one gold support parent retrieved. Quality metrics use offline annotations; they are separate from live ESA.')
    rows = tables[experiment]
    if rows:
        st.dataframe(pd.DataFrame(rows).drop(columns=['Source']), hide_index=True, width='stretch',
                     column_config={'Hit@5': st.column_config.NumberColumn(format='%.4f'),
                                    'Recall@5': st.column_config.NumberColumn(format='%.4f')})
        with st.expander('Artifact paths and availability'):
            st.dataframe(pd.DataFrame(rows), hide_index=True)
            st.write('Null metrics mean unavailable; they are never replaced with zero.')
    else:
        st.warning('No readable saved results for this experiment.')
    if errors:
        with st.expander(f'Artifact loading issues ({len(errors)})', expanded=True):
            for error in errors:
                st.warning(error)
    st.write('Fixed conditions disable query-aware selection and recovery. Query-aware disables recovery; adaptive retains bounded recovery and reassessment. Phase 6A also records trained-router and trained-adaptive comparisons; the selected depth-0 router chooses lexical for every question.')
    st.warning('Experiments have different cohorts/configurations. Do not pool these tables or infer paired differences across them. HotpotQA questions have known exposure; MuSiQue results are development/internal. Retrieval calls and latency are work proxies, not equal-compute or monetary cost. Independent final evaluation, answer-generation evaluation and validated hallucination-reduction claims remain unavailable.')
