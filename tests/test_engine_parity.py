"""
Engine parity test (Strict TDD, task 3.2).

The quiz engine is implemented once in JS. pytest cannot import it, so we run
`node` on a small parity driver that imports quiz-engine.js over a fixture
bank, generates an exam, and prints a determinism + invariant probe as JSON.
The Python side asserts the same invariants the vitest suite checks, proving
the two test worlds agree on the engine contract.

Contract (quiz-mode spec):
- 40 distinct questions, none imageRequired
- señales <= 8, generales >= 20, auto >= 6
- options have bijective displayKeys remapped from a single-character alphabet
- deterministic under a fixed seed
"""
import json
import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
ENGINE = ROOT / "js" / "quiz-engine.js"


@pytest.fixture(scope="module")
def node():
    if not ENGINE.exists():
        pytest.skip("quiz-engine.js not built yet")
    return ENGINE


def run_node(driver: str):
    """Execute a JS snippet with node in the repo root (ESM resolution)."""
    proc = subprocess.run(
        ["node", "--input-type=module", "-e", driver],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    assert proc.returncode == 0, f"node failed:\n{proc.stderr}\n{proc.stdout}"
    return json.loads(proc.stdout.strip().splitlines()[-1])


DRIVER = r"""
import { buildExam, isPass } from './js/quiz-engine.js';

// synthetic bank mirroring the vitest fixture (2 image decoys)
const mkQ = (id, section, category, {essential=false, imageRequired=false} = {}) => ({
  id, number: null, section, category, question: `Question ${id}?`,
  options: [{key:'a',text:`${id}-a`},{key:'b',text:`${id}-b`},{key:'c',text:`${id}-c`}],
  correct: 'b', answerType: 'single', fundamento: `F ${id}`,
  sources: [{material:'manual',ref:'Cap. II',page:null}],
  essential, imageRef: null, imageRequired,
  srcFile:'cuestionario.pdf', srcPage:1, regionNote:null, confidence:0.9, reviewed:true,
});
const bank = [];
for (let i=0;i<60;i++) bank.push(mkQ('sec-'+String(i+1).padStart(4,'0'),'seguridad','generales',{essential:i<5}));
for (let i=0;i<15;i++) bank.push(mkQ('sen-'+String(i+1).padStart(4,'0'),'senales','senales',{essential:i<2}));
for (let i=0;i<10;i++) bank.push(mkQ('aut-'+String(i+1).padStart(4,'0'),'auto','especificas-auto',{essential:i<2}));
bank.push(mkQ('sen-999image','senales','senales',{imageRequired:true}));
bank.push(mkQ('aut-999image','auto','especificas-auto',{imageRequired:true}));

const cfg = { examSize: 40, floors: { senales: 8, generales: 20, auto: 6 } };
const ex = buildExam(bank, cfg, 1234);
const ex2 = buildExam(bank, cfg, 1234);
const alpha = 'abcdefghijklmnopqrstuvwxyz';
const probe = {
  count: ex.questions.length,
  unique: new Set(ex.questions.map(q=>q.id)).size,
  noImage: ex.questions.every(q=>!q.imageRequired),
  byCat: {
    senales: ex.questions.filter(q=>q.category==='senales').length,
    generales: ex.questions.filter(q=>q.category==='generales').length,
    auto: ex.questions.filter(q=>q.category==='especificas-auto').length,
  },
  keysBijective: ex.questions.every(q => {
    const ks = q.options.map(o=>o.displayKey).sort();
    return ks.join('') === alpha.slice(0, q.options.length);
  }),
  noRepeatRender: new Set(ex.questions.flatMap(q=>q.options.map(o=>o.text))).size,
  deterministic: JSON.stringify(ex.questions.map(q=>q.id)) === JSON.stringify(ex2.questions.map(q=>q.id)),
  pass30: isPass(30, 40), fail29: isPass(29, 40),
};
console.log(JSON.stringify(probe));
"""


def test_engine_parity_probe(node):
    probe = run_node(DRIVER)
    assert probe["count"] == 40
    assert probe["unique"] == 40
    assert probe["noImage"] is True
    assert probe["byCat"]["senales"] <= 8
    assert probe["byCat"]["generales"] >= 20
    assert probe["byCat"]["auto"] >= 6
    # sum of categories equals the exam size (no strays)
    assert sum(probe["byCat"].values()) == 40
    assert probe["keysBijective"] is True
    assert probe["noRepeatRender"] == 40 * 3
    assert probe["deterministic"] is True
    assert probe["pass30"] is True
    assert probe["fail29"] is False


def test_engine_parity_floor_deficit(node):
    """TRIANGULATE: auto smaller than its floor -> all auto drawn, residual filled."""
    driver = r"""
import { buildExam } from './js/quiz-engine.js';
const mkQ = (id, section, category, opts={}) => ({ id, number:null, section, category,
  question:`Q ${id}?`, options:[{key:'a',text:`${id}-a`},{key:'b',text:`${id}-b`},{key:'c',text:`${id}-c`}],
  correct:'b', answerType:'single', fundamento:`F ${id}`,
  sources:[{material:'manual',ref:'Cap. II',page:null}], essential:false, imageRef:null,
  imageRequired:false, srcFile:'cuestionario.pdf', srcPage:1, regionNote:null, confidence:0.9, reviewed:true });
const bank = [];
for (let i=0;i<60;i++) bank.push(mkQ('sec-'+String(i+1).padStart(4,'0'),'seguridad','generales'));
for (let i=0;i<15;i++) bank.push(mkQ('sen-'+String(i+1).padStart(4,'0'),'senales','senales'));
for (let i=0;i<2;i++) bank.push(mkQ('aut-'+String(i+1).padStart(4,'0'),'auto','especificas-auto'));
const ex = buildExam(bank, { examSize: 40, floors: { senales: 8, generales: 20, auto: 6 } }, 5);
const auto = ex.questions.filter(q=>q.category==='especificas-auto');
console.log(JSON.stringify({ count: ex.questions.length, autoDrawn: auto.length, autoAll: bank.filter(q=>q.category==='especificas-auto').length }));
"""
    probe = run_node(driver)
    assert probe["count"] == 40
    assert probe["autoDrawn"] == probe["autoAll"] == 2