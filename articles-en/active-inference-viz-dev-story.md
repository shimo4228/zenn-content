---
title: "I Made a Paper I Don't Understand Run in the Browser — Active Inference × Claude Code"
emoji: "🧠"
type: "idea"
topics: ["claudecode", "numpy", "streamlit", "python", "ai"]
published: false
---

In a corner of the AI research report that arrives at 5 AM every morning, there was a term: "Active Inference." The brain maintains an internal model of the world and selects actions to minimize the gap between prediction and reality. A framework that provides a unified explanation for biological perception, action, and decision-making——.

The moment I read it, something snagged.

That same day, I cloned the original paper's code, and from planning to completion in about 2 hours, I stripped out all the PyTorch and rewrote it in pure NumPy, then built an **interactive visualization UI that didn't exist in the original** using Streamlit so anyone could run it in the browser. 1,550 lines. 98% test coverage.

**At the mathematical level, I do not understand the theory.**

---

## I Don't Know Why This Hooked Me

While studying generative AI, I stumbled upon what I mentioned at the top — Active Inference, a theory derived from Karl Friston's Free Energy Principle.

I'll be honest. I lose the thread by the third line of equations. I get variational inference and Bayesian estimation as concepts, but I have no hands-on intuition for them.

And yet the urge to "just make this run" wouldn't go away. One of the dev ideas listed in my daily-research ([automated research report](https://zenn.dev/shimo4228/articles/daily-research-automation)) was "Active Inference visualization tool," and the moment I saw it, my hands started moving.

If you asked me why, I couldn't answer. I was vaguely aware I'd lost my mind while building it.

## The Kind of Thing That's Possible Now

I want to pause here and think about something.

**A computational neuroscience paper was turned into a browser-based visualization tool by someone who doesn't understand the theory.** I rewrote the PyTorch code in NumPy, derived the Jacobian analytically, wrote tests, and built an interactive UI where you can tweak parameters and watch the behavior in real time. It took about 2 hours.

This speaks to the power of Claude Code, and simultaneously to the terror of the era.

"In the age of AI, the only thing that survives is obsession" — you hear this a lot. Skills and knowledge can be replaced by AI, but the irrational fixation of "for some reason, this pulls me in" cannot be replicated. After using Claude Code continuously, I've come to realize this isn't just positioning talk.

With Claude Code, there could be countless people who can build an Active Inference tool. But "someone who snags on a single term buried in their morning research report and starts building without understanding the theory" — there probably aren't that many. In a world where implementation ability has been democratized, the only remaining differentiator is **the obsession that decides what to build.**

This article is a record of that obsession.

---

## The Original Paper and Code — According to Claude Code

The source paper was Priorelli et al. (2025) "[Embodied decisions as active inference](https://journals.plos.org/ploscompbiol/article?id=10.1371/journal.pcbi.1012745)." Published in PLOS Computational Biology, the paper models "embodied decision-making" using Active Inference.

According to Claude Code, the model has four interlocking processes:

1. **Discrete inference** — probabilistically choosing "what to grasp" (POMDP)
2. **Continuous inference** — optimizing "how to move the hand" via predictive coding
3. **Kinematics** — forward kinematics for a 3-joint arm (angles → hand position)
4. **Body** — a physical model that moves the hand according to the brain's beliefs

The original code is written in [PyTorch + Pymunk + Pyglet](https://github.com/priorelli/embodied-decisions). It requires a GPU environment and can't run in the browser. It was research code meant for local experiments — **there was no UI that anyone could just try in a browser.**

## Design Decisions: Why Rewrite It and Put It in the Browser — Says Claude Code

Normally, I don't take Claude Code's proposals at face value. "Why that design?" "What alternatives did you consider?" "What are the trade-offs?" — I ask these every time. I dig into Claude Code's reasoning relentlessly and don't start implementing until I'm convinced. Anyone who's read my previous articles knows this stance.

**This time was different.**

Since I don't understand the underlying theory at all, I have no way to verify why Claude Code said "we should rewrite PyTorch to NumPy." When it said "the Jacobian can be derived in closed form," I didn't understand what a Jacobian is at the mathematical level. "For 3 joints, it becomes a 2×3 matrix" — sure, okay.

The design decision table below is a record of what Claude Code decided. The only things I understood were the motivation "I want to run this on Streamlit Cloud" and "uv is fast."

| Decision | Claude Code's Reasoning | Rejected Alternative |
|------|------|---------------|
| PyTorch → pure NumPy | To run on Streamlit Cloud. For 3 joints, Jacobian can be written in closed form | Keep PyTorch → can't deploy |
| Pymunk → Spring tracking | C bindings won't work on Streamlit Cloud. Replaceable in 8 lines | MuJoCo → overkill |
| frozen dataclass | hashable → `@st.cache_data` works directly. Also prevents accidental mutation of precision parameters | dict → not hashable |
| Plotly > Matplotlib | Interactive features (hover, zoom) and Streamlit compatibility | Matplotlib → static |
| uv | Fast. Self-contained in `pyproject.toml`. `uv run` auto-manages venv | poetry → slow |

<!-- textlint-disable ja-technical-writing/no-doubled-joshi -->
There was exactly one motivation I added on my own. **"If I watch the rewriting process, maybe I'll understand a little."** If I watch Claude Code rewriting from PyTorch to NumPy, I should at least be able to see "what it's computing." In the end, this expectation was half right and half wrong. I could see "what is being computed." But "why it computes that" remains a mystery.
<!-- textlint-enable ja-technical-writing/no-doubled-joshi -->

## The Biggest Stumbling Block: The VJP Sign Was Wrong — Apparently

About 80% of the rewriting went smoothly. I gave Claude Code the paper-notation-to-code-variable mapping table and the original code's structural map as documentation, and it rewrote file by file. I just sat next to it watching. Thinking "huh, so that's how it's structured."

Suddenly, **the simulation values exploded.**

In Claude Code's words, "the extrinsic units (beliefs about hand position) diverged exponentially." What I saw on screen was values ballooning to `1e+15` and hitting `NaN` within a few steps.

When I asked Claude Code, it kept making off-target suggestions like "let's try adjusting parameters." I asked three times and got three different answers. Normally I'd push back — "what's your basis for that?" — but this time I had no reference frame for "the right direction." I couldn't even be truly certain that Claude Code's suggestions were off-target. It's only retrospective inference — they didn't fix the problem, so they were probably wrong.

In the end, by diffing the original paper's code against the implementation, Claude Code identified the cause. **The `-precision` (negative precision matrix) factor that PyTorch's `tensor.backward(eps)` implicitly includes was missing from the manual implementation.**

— And when that was explained to me, all I could say was "I see." Here's the fixed code:

```python
# Unit class in continuous.py — correct NumPy port of PyTorch backward(eps)
# self.x[0]: unit's belief (hand position), self.pi_eta_x: precision parameter
#
# WRONG:   parent.grad += J.T @ eps              ← diverges
# CORRECT: parent.grad += -precision * (J.T @ eps)  ← stable

eps_eta_x = (self.x[0] - fk_pred) * self.pi_eta_x
parent_grad = -self.pi_eta_x * (J.T @ eps_eta_x)  # VJP with -π factor
```

<!-- textlint-disable ja-technical-writing/no-doubled-joshi -->
The difference between `WRONG` and `CORRECT` is obvious if you look. It's whether you attach a minus sign or not. But I can't understand why the minus is necessary.
<!-- textlint-enable ja-technical-writing/no-doubled-joshi --> Claude Code explained that "in predictive coding, the negative sign of the precision matrix is included in the VJP." Since I don't understand predictive coding, I can't judge whether this explanation is correct.

What I could verify was that the fix is numerically correct. Claude Code wrote a test comparing SciPy's numerical differentiation against the analytical Jacobian, confirming agreement at `atol=1e-5`.

```python
# Analytical Jacobian test — comparison with numerical differentiation
def test_jacobian_vs_numerical():
    angles = np.array([0.3, -0.5, 0.1])
    lengths = np.array([0.4, 0.3, 0.2])
    J_analytical = analytical_jacobian(angles, lengths)
    J_numerical = approx_fprime(angles, lambda a: forward_kinematics(a, lengths))
    np.testing.assert_allclose(J_analytical, J_numerical, atol=1e-5)
```

The numbers matching and the theory being correct are different things, but for someone who doesn't understand, this was the only foothold.

## Threw Out the Physics Engine — Claude Code Threw It Out, But Still

The original code simulates arm movement with Pymunk (a 2D physics engine). Since C extensions can't be used on Streamlit Cloud, an alternative was needed.

Claude Code explained it this way:

> The point of Active Inference is that "beliefs drive action." The body just follows the beliefs, and the lag generates prediction error. So a physics engine is unnecessary — 8 lines of spring tracking can replace it.

```python
# simulation.py — spring tracking without a physics engine (8 lines)
BODY_TRACKING_GAIN = 8.0
actual_angles_norm += (believed_angles_norm - actual_angles_norm) * gain * dt
# → The lag between brain beliefs and body generates prediction error, driving the inference loop
```

250MB of PyTorch + Pymunk + Pyglet was replaced by 50MB of NumPy + SciPy + Streamlit. What had been a local-only research script became **a visualization tool you can play with in the browser, tweaking parameters and watching behavior in real time.** Whether this decision is theoretically sound, I don't know. But values labeled "beliefs" change, and the arm moves toward the target. Whether this is the correct behavior for Active Inference — I can't judge.

## Project Structure

Here's the structure of the 1,550 lines Claude Code wrote in 2 hours. In addition to rewriting the computation core, the `viz/` directory and `app.py` are entirely new — they didn't exist in the original code.

```text
src/active_inference_viz/        # 1550 lines
├── model/                        # 1113 lines — math core
│   ├── config.py     (139 lines) — SimConfig (frozen), SimResult
│   ├── math_utils.py (230 lines) — Jacobian, FK, softmax, BMC
│   ├── discrete.py   (176 lines) — discrete inference (POMDP)
│   ├── continuous.py  (258 lines) — predictive coding (Unit/Obs)
│   ├── brain.py      (162 lines) — discrete + continuous coupling
│   └── simulation.py (148 lines) — trial loop
├── viz/                          # 265 lines — visualization
│   ├── theme.py       (58 lines)
│   ├── arm_view.py   (122 lines) — 2D arm display
│   └── belief_panel.py (85 lines) — belief time series
└── app.py            (176 lines) — Streamlit UI

tests/                            # 519 lines, 50 tests, 98% coverage
```

The comments on the right are Claude Code's annotations verbatim. I don't even know what "BMC" stands for (Bayesian Model Comparison, apparently).

## I Don't Know If It's Correct

Tests pass. Numerical differentiation comparisons match. The arm moves on Streamlit. When a cue is presented, beliefs change, and the hand reaches toward the target.

**But I don't know if it's "correct as Active Inference."**

Is the predictive coding update rule theoretically valid? Is the coupling timing between discrete and continuous inference appropriate? Is the EFE (Expected Free Energy) computation correct? I confirmed these against the paper's equations with Claude Code — to be precise, Claude Code confirmed them and said "no issues," and I believed it.

This is worth stating honestly. With Claude Code, you can build something that "works" without understanding the theory. If tests pass and numbers are stable, it looks correct on the surface. But since I lack the ability to judge that quality, it remains an **unverified implementation.**

It's published on GitHub, and I welcome feedback from anyone with expertise in Active Inference.

https://github.com/shimo4228/active-inference-viz

## Why I Couldn't Write This Article for a Week

I write articles about everything I do with Claude Code. Usually the same day or the next. Writing serves as the "Check" in my PDCA cycle and helps my own learning.

This project alone sat untouched for a week.

The reason I couldn't write it was simple: **I couldn't feel that I had learned anything from this project.** Usually I can write "I made this design decision, and here's why" or "I got stuck here, and here's the lesson." Not this time. Claude Code did everything. I sat next to it. I know what happened, but I don't know what I learned.

After a week, I realized that "the absence of learning itself is worth writing about." So here I am.

## Technical Learnings — There Are None

I'll be honest. There are no technical learnings from this development.

The technical content written in this article — VJP, Jacobian, predictive coding, precision matrices, chain rule — I don't understand any of it. I'm just reproducing Claude Code's explanations verbatim. There was never a single moment of "ah, so that's how it works."

If I learned one thing, it's the **bare fact that you can build things without understanding them.** Tests pass, numbers are stable, the arm moves on screen. You look at it and think "done." But if someone says "explain what you built in your own words," I can't say anything beyond what's written in this article.

Whether that counts as learning, I don't know.

## The Age Where Only Obsession Remains

I'm thinking about this again as I write.

Claude Code is a terrifying tool. A layperson turned a computational neuroscience paper into a browser-based visualization tool in 2 hours. Not just rewriting the computation engine, but building an interactive UI that didn't exist in the original — with 98% test coverage and full type checking. Would a professional researcher point out fatal errors? Or would they say "formally, it's well done"? I don't have the ability to judge which.

But "why Active Inference" is something Claude Code can't answer. Among the dozens of topics lined up in the morning research report, why did my hand reach for **this one** of all things? There's no rational explanation. If pressed, I'd say the picture of "the brain holding a model of the world and minimizing the gap between prediction and reality" seemed to suggest something about the relationship between AI and humans — that's about all I can say.

What I realized after finishing the Active Inference project is that in a world where implementation ability has been democratized, **"why do I want to build this"** is far rarer than "what can I build." Irrational fixation — obsession — is the only eigenvalue left to humans.

I don't know if the theory is correctly implemented. But the fact that "I wanted to build it despite not understanding it" — that, at least, is undeniably real.

---

<!-- textlint-disable -->
:::message
**Repository:** https://github.com/shimo4228/active-inference-viz
You can run it interactively in the browser via Streamlit. If you're knowledgeable about Active Inference, I'd love your feedback.
:::
<!-- textlint-enable -->

## References

- Priorelli, M. et al. (2025). "[Embodied decisions as active inference](https://journals.plos.org/ploscompbiol/article?id=10.1371/journal.pcbi.1012745)." PLOS Computational Biology.
- [Original code (PyTorch + Pymunk + Pyglet)](https://github.com/priorelli/embodied-decisions)
- [pymdp — Active Inference for Discrete State Spaces](https://github.com/infer-actively/pymdp)
- [Active Inference Institute](https://www.activeinference.institute/)
