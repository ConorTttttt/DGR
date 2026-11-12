"""ADR 2025 per-agent changed-file ownership check. Make this a REQUIRED CI check after merge."""
import argparse
import fnmatch
import sys

OWNERS={
  "lead/adr2025-contracts-v1":("contracts/v1/**","docs/integration/**","tests/integration/**",".github/workflows/adr2025-contract-ownership.yml"),
  "class1/adr2025-explosives-v1":("agents/class1_explosives/**",),
  "agent1/adr2025-table-a-ingestion":("regulations/adr/2025/table_a_*","regulations/adr/2025/corrigenda_impacts.json","scripts/ingest_adr2025_table_a.py","scripts/validate_adr2025_table_a_output.py","tests/test_adr2025_table_a.py",".github/workflows/adr2025-table-a.yml",".gitignore"),
  "agent2/adr2025-input-model-v0-1":("engine/input_model/adr2025/**",),
  "agent3/adr2025-classification-rules":("agents/agent3/**",),
  "agent4/adr2025-un-assignment-review":("agents/agent4_un_assignment/**",),
  "agent5/execution-framework":("agent5_execution/**",),
}
def check(branch,changed):
    allowed=OWNERS.get(branch)
    if allowed is None:
        return [f"UNREGISTERED_BRANCH:{branch}"] if branch.startswith(("agent","lead/","class1/")) else []
    return [path for path in changed if path.strip() and not any(fnmatch.fnmatchcase(path,glob) for glob in allowed)]
def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--branch",required=True)
    parser.add_argument("--files",required=True)
    opts=parser.parse_args()
    with open(opts.files,encoding="utf-8") as f:
        paths=[x.strip() for x in f if x.strip()]
    violations=check(opts.branch,paths)
    for path in violations:
        print("OWNERSHIP_VIOLATION:",path,file=sys.stderr)
    return 1 if violations else 0
if __name__=="__main__":
    sys.exit(main())
