# Math Skill 二次全面诊断报告（2026-07-08）

> 方法：以独立审稿人视角重读 `main.tex`（557 行）、`README.md`（962 行），并用 `audit_verify.py` 重新核验数据层。
> 本轮**不重复** 2026-07-07 审计报告（C1–C4、M1–M6 已全部修复且回归确认仍在）。
> 重点：**之前两轮（AI 审计 + 用户手动挑刺）都漏掉的问题** + **删 forbid 节/重编号/改链接大改后引入的新不一致**。

---

## 0. 数据层状态（已重验，OK）
- `tab:d4`（n=7–30，含补回的 23/25/26/28/29）、`tab:c4counts`（rot4 n=12–56）、`tab:extinct`（奇数 n=31–45）、轨道结构（n=12/14/16/18/72）全部与本地缓存逐条吻合。
- rot2 计数（n=21/23/25/27/29 = 2412/3967/8980/17332/44828）与缓存一致；n=31 rot2 文件缺失（数据库确实无，非 bug）。
- rct4 存在性（n=9/17/19 有，n=11/13/15 无）与缓存一致。
- **结论：所有数值声明可信，问题集中在叙事/事实/内部一致性层面。**

---

## 1. 严重问题（🔴 之前漏掉，本轮新发现）

### D1. 事实错误：D(n) 经典已知上界写成 n=46（应为 n=52）
- `main.tex` L84：「For many years, the precise values of D(n) were known only up to n=46.」
- 但 `README.md` L11 自己写：「2n-point solutions have been found for all n ≤ 52 (classical result)」；Flammenkamp 数据库经典上界就是 n=52。
- **矛盾**：论文与自己的 README 直接冲突；且 n=46 是事实错误（应为 52）。
- 影响：审稿人一眼能戳穿，损害可信度。

### D2. “D₄ 分析到 n=53” 在论文内部无对应表格支撑（声明与数据脱节）
- 摘要 L73、贡献 L110、结论 L545 均写「D₄-inequivalent analysis **through n=53** (catalogued classes)」。
- 但论文实际表格：
  - `tab:d4`（L182–217）只到 **n=30**
  - `tab:extinct`（L414–432）奇数只到 **n=45**
  - `tab:c4counts`（L227–249）rot4 到 n=56，但那是 rot4 计数不是 D₄ missing-center 表
- 读者看到「through n=53」会期待论文有 n=31–53 的 D₄ missing-center 数据，但**论文里没有**（只有 README 有）。
- 这是上一轮审计 M5 的**遗留 gap**：当时只把文字从「n=30」改成「n=53」，没同步扩展表格。
- 修复建议（二选一）：(a) 把 `tab:d4` 扩展到 n=53（README 已有完整数据，直接搬）；(b) 文字改为论文实际覆盖范围（D₄ 表 n=30，奇数 extinction n=45，rot4 n=56）。

### D3. 重建精度夸大：论文说 <0.1%，README 承认 0.8%
- `main.tex` L471：「Cross-validation ... confirms the reconstruction is exact (all match within sampling error <0.1%).」
- `main.tex` L481 注脚：「verified exact within 0.1% sampling error」
- 但 `README.md` L730：「Cross-validation ... matches ... for n=7-13 (n=9: 368 C++ vs 365 reconstruction, **within 0.8%**).」
- **矛盾**：同一仓库，同一 n=9 重建，论文说 <0.1%、README 说 0.8%。论文的 0.1% 不实（实际 n=9 差 3 个，0.8%）。
- 影响：把近似重建说成「exact / <0.1%」是夸大，且自相矛盾。

### D6. 数学错误：把「D₄ 轨道强制 ≥4 点/环」说成普遍真理（实际只有 rct4/C₄ 轨道大小=4）
- `main.tex` L462：「rct4 solutions invariably have the grid center as a circumcenter. This is a group-theoretic necessity: **D₄ orbits on odd-n grids force ≥4 points per distance ring.**」
- **错误**：D₄ 群包含多种对称类，轨道大小不一：
  - iden 轨道大小 = 1
  - rot2 / dia1 / ort1 轨道大小 = 2
  - rot4 / rct4 轨道大小 = 4
  - dia2 轨道大小 = 1 或 2（对角点固定 + 非对角点成对）
  - 所以「D₄ orbits force ≥4」是**错的**——只有 rct4（及 C₄）轨道大小=4。
- 连带错误 L286：「even n≥32 ... only rot4 and dia survive, **necessarily contain the center by group theory**」——把 dia2 也说成 group-theoretic necessity。但 `README.md` L682 正确指出：「dia2 solutions ... also universally have the center as circumcenter, **though a formal proof for dia2 is not yet established**」。
- **矛盾 + 数学错误**：论文把 dia2 的经验观察说成群论必然（与 README 冲突），且 L462 的「D₄ orbits ≥4」前提本身错误。
- 修复：L462 改「rct4 (and C₄) orbits, size 4, force ≥4 points per ring」；L286 对 dia2 改回「empirically observed, formal proof pending」（与 README 一致）。

---

## 2. 中等问题（🟡 之前漏掉 / 大改残留）

### D4. n=18 距离环数写成单值 8，应为 8–9
- `tab:c4evol` L351：「18 | 9 | **8** | Yes | 4 or 8」
- 验证脚本输出：「n=18: rings min/max=**8/9**」
- 上一轮审计 M4 已要求 ring 数给范围（n=14 改 6–7、n=16 改 7–8），但 **n=18 漏改**，仍写单值 8。应为 8–9。

### D5. n=72 是 n=18 的 4×，论文写 6×
- `main.tex` L365：「persist at n=72, a scale **6× larger than the next-largest analyzed (n=18)**」
- 72 / 18 = **4**，不是 6。6× 是相对 n=12（72/12=6，README L521 正确写「6× larger than n=12」）。
- 论文括号明确写 (n=18)，故 6× 是计算错误。

### D7. `tab:fullrecon` 重建值缺 ~ 符号（与自身注脚矛盾）
- `tab:fullrecon`（L487–506）n=14–20 写精确值（如 14 | 10568 | 84），无 ~。
- 但 L481 注脚承认：「values for n≥14 are **reconstructed** from D₄-inequivalent counts via the orbit multipliers」。
- 上一轮审计去掉了 18/19/20 的 ~，但 n=14–20 全是重建估计，应统一标 ~（或至少 n≥14 全标）。当前 n=14 写 84，README L743 写 ~85——差 1，且论文把估计当精确。
- 修复：n≥14 全加 ~，或正文明确「reconstructed estimate」。

---

## 3. 轻微问题（🟢 之前漏掉）

- **D8**：`tab:c4counts` L246「54---56 (see text)」格式怪异（应为「54–56 (see text)」或分两行）。
- **D9**：L454「classic SAT phase transition analogous to the well-known random k-SAT threshold」——rot2 约束图是高度结构化的（非随机），类比 random k-SAT 可能误导，建议改为「structured combinatorial threshold」。
- **D10**：L404「D(n)=2n for all even n is **effectively established**」——对未证猜想略强，建议「strongly supported by structural + computational evidence」。
- **D11**：L286「rot4 and **dia**」中「dia」模糊（应为 dia2），且与 L668–674（README）的对称类列表不符。

---

## 4. README 额外发现（不在论文内，但同仓库）

- **R1**：`README.md` L499「Zero exceptions in **33,634** tested solutions」应为 **33,534**（论文 L813 写 33,534，且 n=12..56 rot4 总和 = 33,534）。差 100，数字错误。

---

## 5. 上一轮审计修复回归确认（✅ 全部仍在）

| 项 | 状态 | 位置 |
|---|---|---|
| C1 rot2 44,828→0 | ✅ | L434, L546 |
| C2 猜想限定 12≤n≤30 | ✅ | L282–284 |
| C3 declining rate | ✅ | L545 |
| C4 D4 表补 5 行 | ✅ | L207–213 |
| M1 iden recorded | ✅ | L220 |
| M2 m∈[10,36] | ✅ | L144 |
| M3 structural patterns | ✅ | L357 |
| M5/M6 n=53 / Heule note | ✅ 文字在，但见表缺口 D2 | L73,110,342,545 |
| forbid-accumulator 整节删除 | ✅ | 无残留（grep forbid=0） |
| 链接 aujurd22 | ✅ | L551 |

---

## 6. 优先级建议

1. **必须修（严重）**：D1（事实）、D2（声明/数据脱节）、D3（夸大）、D6（数学错误）。这四条任何一条被审稿人发现都会危及论文可信度。
2. **应该修（中等）**：D4、D5、D7——都是具体数字/符号错误，改起来快。
3. **可改可不改（轻微）**：D8–D11。
4. **README 同步**：R1 + 之前已修的 Implementation 节删除，README 现在整体可信，只剩 R1 一个数字。

**最关键的修复路径**：以 D2 为枢纽——要么把 `tab:d4` 扩展到 n=53（一劳永逸解决 D2 + 让摘要/贡献/结论的 n=53 有支撑），要么把三处文字改回论文实际覆盖范围。建议选 (a) 扩展表格，因为数据现成（README + 缓存都有）。

---

*诊断完成。本轮新发现问题 11 项（D1–D11）+ README 1 项（R1），其中 4 项严重。上一轮修复全部回归确认有效。*
