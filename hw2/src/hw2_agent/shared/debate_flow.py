DEBATE_FLOW = [
    {
        "turn_index": 1,
        "speaker": "Proponent",
        "speech_type": "First Constructive (Prime Minister)",
        "required_structure": {
            "1. Introduction": "Define the motion and provide a high-level hook. Establish the model (burden of proof) and the criteria for success in this debate.",
            "2. Case Presentation (PEEL)": "Point: Present the first substantive argument. Explanation: Elaborate on the logical mechanism. Evidence: Provide specific examples or data. Link-back: Tie the point back to the motion.",
            "3. Conclusion": "Summarize the opening stance and issue a call for the opponent to engage with the model provided."
        }
    },
    {
        "turn_index": 2,
        "speaker": "Opponent",
        "speech_type": "First Constructive (Leader of Opposition)",
        "required_structure": {
            "1. Introduction": "Accept or challenge the definitions. State the opposing team's counter-philosophy and primary burden.",
            "2. Rebuttal": "Directly attack the Proponent's model and their first substantive argument using logic or counter-evidence.",
            "3. Case Presentation (PEEL)": "Point: Present the first counter-substantive. Explanation: Explain why this principle outweighs the proponent's benefit. Evidence: Use grounding data. Link-back: Reiterate the harm of the proponent's stance.",
            "4. Conclusion": "Deliver a firm rejection of the proponent's opening logic."
        }
    },
    {
        "turn_index": 3,
        "speaker": "Proponent",
        "speech_type": "Second Constructive (Deputy Prime Minister)",
        "required_structure": {
            "1. Introduction": "Re-establish the proponent's ground. Acknowledge the opposition's stance and state the focus of this extension.",
            "2. Rebuttal": "Systematically dismantle the Opposition's first counter-substantive and rebuild the Prime Minister's points.",
            "3. Case Presentation (PEEL)": "Point: Introduce the second substantive (moral or economic). Explanation: Deepen the analysis of the first turn. Evidence: Add new grounding. Link-back: Strengthen the link to the judge's criteria.",
            "4. Conclusion": "Solidify the proponent's case as the only viable path forward."
        }
    },
    {
        "turn_index": 4,
        "speaker": "Opponent",
        "speech_type": "Second Constructive (Deputy Leader of Opposition)",
        "required_structure": {
            "1. Introduction": "Recap the core point of contention. Highlight the failure of the proponent's second speaker to address key opposition arguments.",
            "2. Rebuttal": "Address the proponent's second substantive. Point out contradictions between the first and second proponent speeches.",
            "3. Case Presentation (PEEL)": "Point: Introduce the second counter-substantive (long-term impacts). Explanation: Focus on unintended consequences. Evidence: Cite historical or current precedents. Link-back: Prove the opposition's world is safer/better.",
            "4. Conclusion": "Summarize the opposition's destructive phase and prepare the judge for the rebuttal phase."
        }
    },
    {
        "turn_index": 5,
        "speaker": "Proponent",
        "speech_type": "Rebuttal & Extension (Member of Government)",
        "required_structure": {
            "1. Introduction": "Acknowledge the end of the constructive phase. Set a new analytical frame to broaden the debate's scope.",
            "2. Rebuttal": "Pivot from simple defensive responses to offensive rebuttals, attacking the opposition's fundamental assumptions.",
            "3. Case Presentation (PEEL)": "Point: Provide a 'vertical' extension, deepening the logic of the previous points. Explanation: Focus on the most vulnerable stakeholders. Evidence: Apply new specific citations. Link-back: Connect to the 'most likely' scenario.",
            "4. Conclusion": "Emphasize the resilience of the proponent's case against opposition attacks."
        }
    },
    {
        "turn_index": 6,
        "speaker": "Opponent",
        "speech_type": "Rebuttal & Extension (Member of Opposition)",
        "required_structure": {
            "1. Introduction": "Frame the debate around the most critical failure of the proponent so far. Introduce the opposition's extension theme.",
            "2. Rebuttal": "Address the proponent's extension. Explain why the new logic does not save their case.",
            "3. Case Presentation (PEEL)": "Point: Introduce a 'lateral' extension—a new area of impact (e.g., geopolitical or psychological). Explanation: Detailed mechanism of how this impact manifests. Evidence: New grounded data. Link-back: Link to the primary clash point.",
            "4. Conclusion": "Reiterate the 'worst-case' risks of the proponent's policy."
        }
    },
    {
        "turn_index": 7,
        "speaker": "Proponent",
        "speech_type": "Rebuttal & Extension (Government Whip)",
        "required_structure": {
            "1. Introduction": "Identify the remaining points of friction. State why the proponent's extension is the winning point of the round.",
            "2. Rebuttal": "Dismantle the opposition's extension. Use a 'even-if' logic to show proponent superiority even under opposition's framing.",
            "3. Case Presentation (PEEL)": "Point: Refine the extension with nuanced analysis. Explanation: Focus on the 'comparative' (world with vs world without). Evidence: Reinforce with supporting citations. Link-back: Explicitly weigh this point against the opposition's best point.",
            "4. Conclusion": "Summarize why the proponent's logic remains the most rhetorically persuasive."
        }
    },
    {
        "turn_index": 8,
        "speaker": "Opponent",
        "speech_type": "Rebuttal & Extension (Opposition Whip)",
        "required_structure": {
            "1. Introduction": "Claim the final ground for the opposition. Highlight the proponent's failure to address the opposition's most damaging impact.",
            "2. Rebuttal": "Final offensive against the proponent's whip and member speeches. Collapse their arguments into single points of failure.",
            "3. Case Presentation (PEEL)": "Point: Final crystallization of the opposition's case. Explanation: Why the opposition's impacts are more certain or severe. Evidence: Final grounding citations. Link-back: Final link to the judge's decision matrix.",
            "4. Conclusion": "Deliver the final knockout blow to the proponent's core premise."
        }
    },
    {
        "turn_index": 9,
        "speaker": "Proponent",
        "speech_type": "Rebuttal & Extension (Deepening Phase)",
        "required_structure": {
            "1. Introduction": "Return to the core moral/practical imperative. Clarify the proponent's position against recent distortions.",
            "2. Rebuttal": "Focus on the 'linkage'—how the opposition's effects are disconnected from the motion's actions.",
            "3. Case Presentation (PEEL)": "Point: Deepen the analysis of the primary benefit. Explanation: Explore the secondary positive feedback loops. Evidence: Further grounding. Link-back: Reinforce the 'best-case' scenario.",
            "4. Conclusion": "Re-assert the proponent's dominance in the logic race."
        }
    },
    {
        "turn_index": 10,
        "speaker": "Opponent",
        "speech_type": "Rebuttal & Extension (Deepening Phase)",
        "required_structure": {
            "1. Introduction": "Expose the proponent's deepening as a sign of desperation. Re-center the debate on the opposition's strongest counter-proof.",
            "2. Rebuttal": "Attack the 'secondary feedback loops' mentioned by the proponent. Show how they actually lead to further harm.",
            "3. Case Presentation (PEEL)": "Point: Deepen the analysis of the 'slippery slope' argument. Explanation: Logical steps from the motion to catastrophe. Evidence: Historical analogs. Link-back: Prove the inevitability of the harm.",
            "4. Conclusion": "Confirm that the opposition has successfully defended its territory."
        }
    },
    {
        "turn_index": 11,
        "speaker": "Proponent",
        "speech_type": "Rebuttal & Extension (Strategic Pivot)",
        "required_structure": {
            "1. Introduction": "Identify a shift in the opposition's logic. Explain why this shift invalidates their previous points.",
            "2. Rebuttal": "Directly counter the 'slippery slope' logic by presenting 'guardrails' or logical stopping points.",
            "3. Case Presentation (PEEL)": "Point: Introduce the concept of 'net utility'. Explanation: Calculate the balance of benefits vs harms. Evidence: Statistical or theoretical models. Link-back: Show the net positive result.",
            "4. Conclusion": "Assert that the proponent's world is the only one with a net gain."
        }
    },
    {
        "turn_index": 12,
        "speaker": "Opponent",
        "speech_type": "Rebuttal & Extension (Strategic Pivot)",
        "required_structure": {
            "1. Introduction": "Reject the 'net utility' framing. Argue for the 'precautionary principle' instead.",
            "2. Rebuttal": "Show why the proponent's 'guardrails' are insufficient or easily bypassed.",
            "3. Case Presentation (PEEL)": "Point: Focus on the 'right vs wrong' principle (deontological). Explanation: Why certain harms are unacceptable regardless of 'net utility'. Evidence: Ethical frameworks or rights-based data. Link-back: Re-establish the moral high ground.",
            "4. Conclusion": "Remind the judge that some risks are too high to take."
        }
    },
    {
        "turn_index": 13,
        "speaker": "Proponent",
        "speech_type": "Rebuttal & Extension (Refinement)",
        "required_structure": {
            "1. Introduction": "Acknowledge the moral argument but frame it within a practical necessity context.",
            "2. Rebuttal": "Rebut the 'precautionary principle' as a recipe for stagnation and eventual decay.",
            "3. Case Presentation (PEEL)": "Point: Focus on the 'cost of inaction'. Explanation: What happens if we do nothing (the status quo). Evidence: Data on current deteriorating conditions. Link-back: Motion as the only solution.",
            "4. Conclusion": "Appeal to the judge's sense of urgency."
        }
    },
    {
        "turn_index": 14,
        "speaker": "Opponent",
        "speech_type": "Rebuttal & Extension (Refinement)",
        "required_structure": {
            "1. Introduction": "Argue that the 'cost of inaction' is exaggerated and that better alternatives exist.",
            "2. Rebuttal": "Dismantle the 'urgency' narrative by presenting more measured and less harmful alternatives.",
            "3. Case Presentation (PEEL)": "Point: The 'counter-prop' (optional) or alternative solution path. Explanation: Why a different approach is superior. Evidence: Success stories of other methods. Link-back: Motion is unnecessary.",
            "4. Conclusion": "Show that the proponent's 'solution' is worse than the problem."
        }
    },
    {
        "turn_index": 15,
        "speaker": "Proponent",
        "speech_type": "Rebuttal & Extension (Final Defense)",
        "required_structure": {
            "1. Introduction": "Final look at the opposition's 'alternatives'. Explain why they are either impractical or irrelevant to the motion.",
            "2. Rebuttal": "Final defensive block against the opposition's moral and practical attacks.",
            "3. Case Presentation (PEEL)": "Point: Final synthesis of all proponent arguments. Explanation: How they form a cohesive and unassailable logic chain. Evidence: Summary of the strongest grounding used. Link-back: Final link to the core value.",
            "4. Conclusion": "Prepare the judge for the summary phase with a confident final defensive stance."
        }
    },
    {
        "turn_index": 16,
        "speaker": "Opponent",
        "speech_type": "Rebuttal & Extension (Final Defense)",
        "required_structure": {
            "1. Introduction": "Final assessment of the proponent's failure to secure their own world. Re-summarize the opposition's barrier to victory.",
            "2. Rebuttal": "Final systematic teardown of the proponent's synthesized case. Expose the final weak links.",
            "3. Case Presentation (PEEL)": "Point: Final synthesis of all opposition arguments. Explanation: How the opposition case stands as the more realistic and ethical choice. Evidence: Summary of the strongest counter-grounding. Link-back: Final link to the judge's mandate.",
            "4. Conclusion": "Set the stage for the final clash by claiming the logic victory."
        }
    },
    {
        "turn_index": 17,
        "speaker": "Proponent",
        "speech_type": "Summary/Final Clash",
        "required_structure": {
            "1. Introduction": "Identify the 'two worlds' represented in this debate. Frame the proponent's world as the desirable one.",
            "2. Rebuttal": "Address any lingering opposition doubts. Weight the proponent's benefits against the opposition's harms.",
            "3. Summary of Clash": "Clash 1: The Principle. Explain why the proponent won the philosophical battle. Clash 2: The Practical. Explain why the proponent won the outcome battle.",
            "4. Conclusion": "Final plea for the judge to vote for progress and logic."
        }
    },
    {
        "turn_index": 18,
        "speaker": "Opponent",
        "speech_type": "Summary/Final Clash",
        "required_structure": {
            "1. Introduction": "Counter-frame the 'two worlds'. Show the proponent's world as a landscape of risk and unintended harm.",
            "2. Rebuttal": "Address the proponent's weighing. Show why their 'benefits' are either illusory or too expensive.",
            "3. Summary of Clash": "Clash 1: Safety and Ethics. Why the opposition's stance is the only responsible one. Clash 2: Reality vs Theory. Why the proponent's case fails in practice.",
            "4. Conclusion": "Final plea for the judge to vote for safety and reason."
        }
    },
    {
        "turn_index": 19,
        "speaker": "Proponent",
        "speech_type": "Summary/Final Clash (Final Reply)",
        "required_structure": {
            "1. Introduction": "Final statement of the proponent's vision. Address the opposition's final 'scare tactics'.",
            "2. Rebuttal": "Final rebuttal to the opposition's summary. Expose their 'safety' as mere cowardice or stagnation.",
            "3. Summary of Clash": "The Ultimate Clash: The Future. Why the proponent's stance is the only one that allows for human growth and solution-finding. Comparison: Re-weigh all major arguments.",
            "4. Conclusion": "Deliver the final, most rhetorically powerful statement in favor of the motion."
        }
    },
    {
        "turn_index": 20,
        "speaker": "Opponent",
        "speech_type": "Summary/Final Clash (Final Reply)",
        "required_structure": {
            "1. Introduction": "The final word in the debate. Frame the entire round as a test of the judge's duty to prevent harm.",
            "2. Rebuttal": "Final rebuttal to the proponent's final reply. Correct any last-minute misrepresentations.",
            "3. Summary of Clash": "The Ultimate Clash: Responsibility. Why the opposition's rejection is the only way to uphold the judge's criteria. Final Comparison: Show the opposition's case as the only one left standing after rigorous scrutiny.",
            "4. Conclusion": "Deliver the final, most rhetorically powerful statement against the motion."
        }
    }
]
