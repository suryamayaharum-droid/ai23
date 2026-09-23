def publication_gate(asset,qc=None,truth=True,canonical=True):
    reasons=[]
    if asset.get("license_status") not in {"approved","owned","original"}: reasons.append("license_not_approved")
    if not truth: reasons.append("truth_gate_failed")
    if not canonical: reasons.append("canonical_gate_failed")
    if qc and qc.get("status") not in {"pass","approved"}: reasons.append("qc_not_approved")
    return {"pass":not reasons,"reasons":reasons}
