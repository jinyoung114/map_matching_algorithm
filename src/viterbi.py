from .candidates import build_balltree, get_candidates
from .transition import emit_prob, trans_prob_strict


def run_viterbi_strict(clean_df, nodes_df, G):
    tree = build_balltree(nodes_df)
    gps2 = clean_df.copy()
    gps2["Candidates"] = [get_candidates(i, gps2, nodes_df, tree) for i in range(len(gps2))]

    viterbi = []
    first = gps2.iloc[0]["Candidates"]
    for c in first:
        c["delta"] = emit_prob(c["Distance"])
        c["psi"] = None
    viterbi.append(first)

    for t in range(1, len(gps2)):
        prev = viterbi[t - 1]
        curr = gps2.iloc[t]["Candidates"]
        for c in curr:
            best, bestp = -1.0, None
            for p in prev:
                tp = trans_prob_strict(
                    G,
                    p,
                    c,
                    (gps2.iloc[t - 1]["Latitude"], gps2.iloc[t - 1]["Longitude"]),
                    (gps2.iloc[t]["Latitude"], gps2.iloc[t]["Longitude"]),
                    gps2.iloc[t]["_dt"],
                    gps2.iloc[t]["_heading"],
                )
                prob = p["delta"] * tp * emit_prob(c["Distance"])
                if prob > best:
                    best, bestp = prob, p
            c["delta"] = best
            c["psi"] = bestp
        viterbi.append(curr)

    last = max(viterbi[-1], key=lambda x: x["delta"])
    path = [last]
    for _ in range(len(gps2) - 1, 0, -1):
        path.insert(0, path[0]["psi"])
    return gps2, path
