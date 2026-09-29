from sce.research.bitcoin_coherence_episodes import summarize_coherence_episodes

def test_episode_summary_separates_true_and_false():
    rows=[
        {"classification":"transition_associated","duration_days":4,"min_coherence":.2,"depth":.25,"lead_days":2},
        {"classification":"transition_associated","duration_days":8,"min_coherence":.3,"depth":.15,"lead_days":4},
        {"classification":"false_alarm","duration_days":2,"min_coherence":.4,"depth":.05,"lead_days":None},
    ]
    s=summarize_coherence_episodes(rows)
    assert s["transition_associated"]["median_duration_days"]==6
    assert s["transition_associated"]["median_lead_days"]==3
    assert s["false_alarm"]["median_depth"]==.05
