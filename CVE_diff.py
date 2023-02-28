import sqlite3
import subprocess
from pathlib import Path 
from git import Repo
import hashlib
Work_Dir = "/tmp/n132_CVEFixes/"
CVE_Diff_Dir = "/tmp/n132_CVE_Diff/"
def md5(s):
    return hashlib.md5(s).hexdigest()
def grab_simple_fixes():
    con = sqlite3.connect("./Output/CVEfixes.db")
    cur = con.cursor()
    res = cur.execute("SELECT hash FROM file_change")
    hashes1 = res.fetchall()
    res = cur.execute("SELECT hash FROM fixes")
    hashes2 = res.fetchall()
    hashes1     = [ x[0] for x in hashes1 ]
    target      = []
    for x in set(hashes2):
        if hashes1.count(x[0]) == 1:
            target.append(x[0])
    simple_fixes = [] 
    for x in target:
        res = cur.execute(f"SELECT * FROM fixes where hash=='{x}'").fetchall()[0]
        simple_fixes.append(res)
    return simple_fixes
def grab_vul_code(meta):
    tag     = meta[0]
    commit  = meta[1]
    repo    = meta[2]
    code_dir = Path(Work_Dir) / ("n132_"+md5(repo.encode()))
    print(code_dir)
    if not code_dir.exists():
        print(f"[+] Clone the repot {repo} (it may take a while)")
        try:
            Repo.clone_from(repo, code_dir)
        except:
            print(f"[!] Fail to clone the repo: {repo}")
            return 
    else:
        print(f"[+] There is a copy of the repo at {code_dir}. Skip `git clong`")
    diff = subprocess.run(f"git diff {commit}^ {commit}".split(),cwd=code_dir,capture_output=True).stdout
    with open(Path(CVE_Diff_Dir)/f"{tag}.diff",'ab+') as f:
        f.write(diff)
    print(f"[+] {Path(CVE_Diff_Dir)}/{tag}.diff")
def simple_fixes():
    res = grab_simple_fixes()
    for _ in res:
        grab_vul_code(_)
    return
if __name__   == "__main__":
    print(f"[+] This script would download related repo to {Work_Dir}\nAll diff files are stored at {CVE_Diff_Dir}")
    input("Press any key to continue")
    simple_fixes()
