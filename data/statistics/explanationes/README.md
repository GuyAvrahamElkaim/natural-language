**This contains explanaations on syntax encode (representations)**
**Explaining syntax encode for constituency syntax**

**Explaining the syntax**

The string consists of segments separated by `|`, with each segment representing a sentence. The format follows `s<i>:ClauseType(Function1+Function2+...)`, where `s<i>` is the sentence index.

The clause code `Way0` corresponds to a narrative clause with a 'wayyiqtol' verb (past narrative form). `xQtX` might be a qatal clause (past tense, non-consecutive).

Key to remember: each code signals a conjunction, verb form, and possibly polarity, rooted in BHSA annotation structure. Each clause defines its role with functions like `Conj`, `Pred`, `Subj`.


### How to read a **constituency‑syntax encode** string

Example row (taken from the `constituency_signature` column):

```
s0:Way0(Conj+Pred+Cmpl)|
s1:Way0(Conj+Pred+Loca)|
s2:xQtX(Conj+Pred+Subj)|
s3:Way0(Conj+Pred+Cmpl)|
s4:Way0(Conj+Pred+Cmpl)|
s5:Way0(Conj+Pred+Cmpl) , none
```

Only the part **before the comma** (bold‑italic below) is the syntax encode; the part after the comma (`none`, or `J`, `P`, `E`, `R`) is the DH‑source label.

---

#### 1 ▪ Sentence index (`s0`, `s1`, …)

* `s<i>` identifies the **i‑th sentence** (0‑based) inside the verse.
  A single Biblical verse can contain multiple grammatical sentences.

---

#### 2 ▪ Clause‑type code (`Way0`, `xQtX`, etc.)

A 4‑character code taken from the ETCBC/BHSA clause annotation:

| Position | Meaning                                                                                                                                                                | Example                                                  |
| -------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------- |
| 1        | **Conjunction**: `W` = **waw** + verb, `A` = other conjunction, `x` = none                                                                                             | `W` in **Way0**                                          |
| 2‑3      | **Verbal form** (or clause kernel): <br>`ay` = wayyiqtol (narrative imperfect)<br>`Qt` = **qatal** (perfect)<br>`yi` = yiqtol (imperfect)<br>`Pt` = participle<br>etc. | `ay` in **Way0** = wayyiqtol<br>`Qt` in **xQtX** = qatal |
| 4        | **Polarity / mood / extra flag**: `0` = default, `X` = neutral/other, `N` = negative, etc.                                                                             | `0` in **Way0**                                          |

So:

* **`Way0`** = a **waw‑consecutive wayyiqtol main clause** (“and he did X…”).
* **`xQtX`** = a **qatal** clause **without a conjunction**.

(You may meet other codes such as `Ptc0` (participle), `yiqt`, etc.; the same rules apply.)

---

#### 3 ▪ Phrase‑function list (`Conj+Pred+Cmpl`)

Inside each clause, the main phrases are listed **in surface order**:

| Abbrev. | Function                                                                             | Typical content                                     |
| ------- | ------------------------------------------------------------------------------------ | --------------------------------------------------- |
| `Conj`  | Conjunction / linker                                                                 | ו‑ / כִּי / אֲשֶׁר…                                 |
| `Pred`  | Predicate                                                                            | Main verb phrase                                    |
| `Subj`  | Subject                                                                              | NP that performs the action                         |
| `Objc`  | Object                                                                               | Direct or indirect object                           |
| `Cmpl`  | Complement                                                                           | Prepositional or second object required by the verb |
| `Loca`  | Locative                                                                             | Place phrase (“in the wilderness”)                  |
| `Time`  | Temporal                                                                             | Time phrase (“at dawn”)                             |
| …       | *(others appear in the data: `PrAd` (predicative adjunct), `Rela` (relative), etc.)* |                                                     |

Thus:

* **`(Conj+Pred+Cmpl)`** → the clause contains, in order:

    1. a conjunction (`Conj` = usually ו־),
    2. the predicate verb phrase,
    3. a required complement (often an object, PP, or accusative marker).

* **`(Conj+Pred+Loca)`** → conjunction, predicate, *then* a locative phrase.

---

### Putting it all together — reading the example line

| Part                          | Meaning                                                                                                                                       |
| ----------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------- |
| **`s0:Way0(Conj+Pred+Cmpl)`** | Sentence 0 is a *wayyiqtol* narrative clause (waw‑consecutive imperfect). It consists of conjunction + predicate + complement.                |
| **`s1:Way0(Conj+Pred+Loca)`** | Sentence 1 is another wayyiqtol clause, but its final phrase is locative.                                                                     |
| **`s2:xQtX(Conj+Pred+Subj)`** | Sentence 2 is an *independent qatal* clause without conjunction; phrase order is conjunction, predicate, subject (e.g., “and he *had* … he”). |
| **`s3` – `s5`**               | Three more wayyiqtol clauses, each Conj + Pred + Cmpl.                                                                                        |
| **`, none`**                  | No Documentary‑Hypothesis source label was assigned to this verse (it is ‘none’).                                                             |

Because the encode string removes every lexical detail and keeps **only** this abstract skeleton, *any two verses whose strings are identical share exactly the same sentence count, clause types, and internal phrase functions in the same order.*

### How to read a **dependency‑syntax encode** string

Example row from the `syntax_signature` column:

```
0:root->‑1|1:nsubj->0|2:case:acc->4|3:punct->5|4:obj->0|5:advcl->0|
6:obj->5|7:obl->5|8:nmod->7|9:conj->7|10:case:acc->12|11:punct->12|
12:obj->9|13:advmod->12|14:punct->15|15:nsubj->0|16:nmod->15|
17:obj->9|18:punct->17 , J
```

Only the part **before the comma** (bold‑italic below) is the encode itself; the part after the comma (`J`, `P`, `none`, …) is the DH‑source label.

---

#### 1 ▪ Triples separated by `|`

Each clause *childIdx\:depFunc→headIdx* describes **one arc** in the Universal‑Dependencies tree.

* **childIdx** – 0‑based position of the token in the verse.
* **depFunc** – UD relation label (`nsubj`, `obj`, `obl`, …); compound labels such as `case:acc` mean a subtype (`case` with accusative).
* **headIdx** – index of the token’s syntactic head. `‑1` marks the sentence **root**.

Because triples are **sorted by childIdx**, the string is deterministic and can be hashed or compared.

---

#### 2 ▪ Reading the example line quickly

| Triple          | Means                                                        |
| --------------- | ------------------------------------------------------------ |
| `0:root->‑1`    | Token 0 is the **root** of the sentence.                     |
| `1:nsubj->0`    | Token 1 is the **nominal subject** of token 0.               |
| `2:case:acc->4` | Token 2 is the accusative marker (`את`) attached to token 4. |
| `3:punct->5`    | Token 3 is punctuation linked to token 5.                    |
| `4:obj->0`      | Token 4 is the **object** of the root verb (token 0).        |
| `5:advcl->0`    | Token 5 heads an **adverbial clause** attached to the root.  |
| `6:obj->5`      | Token 6 is the object inside that adverbial clause.          |
| `7:obl->5`      | Token 7 is an **oblique** (prep‑phrase) inside the advcl.    |
| `8:nmod->7`     | Token 8 is a nominal modifier of the oblique.                |
| `9:conj->7`     | Token 9 is a **conjoined** phrase coordinated with token 7.  |
| …               | *(continues in the same way)*                                |

Because **no lexical information is stored**, any verse producing this exact string must have:

* the same number of tokens (indices 0‑18 here),
* the *same dependency function* at each position, and
* the *same graph shape* (each head matches).

Thus two verses are structurally identical *iff* their encode strings are identical.

---

#### 3 ▪ Comma‑suffix = DH source

The trailing `, J` in this row means the verse is labelled **“J”** in the Documentary‑Hypothesis sources table. If no label exists, the suffix is `, none`.

---

> **Quick mnemonic**
> `child:func->head` ⇢ “child token at *child* carries relation *func* to *head*.”
