#!/usr/bin/env python3
"""Lokale, isolerede tests. Koerer IKKE deployment mod vaertens /etc."""
import base64, importlib.util, os, pathlib, shutil, subprocess, sys, tempfile, unittest
ROOT=pathlib.Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('validate',ROOT/'tools/validate_config.py')
v=importlib.util.module_from_spec(spec);spec.loader.exec_module(v)
spec2=importlib.util.spec_from_file_location('scope',ROOT/'tools/netplan_scope.py')
n=importlib.util.module_from_spec(spec2);spec2.loader.exec_module(n)
def run(*cmd, **kw):
    return subprocess.run(cmd, text=True, capture_output=True,timeout=15,**kw)
class BundleTests(unittest.TestCase):
    def test_all_bash_syntax(self):
        for f in ROOT.rglob('*.sh'):
            with self.subTest(file=str(f.relative_to(ROOT))):
                r=run('bash','-n',str(f));self.assertEqual(r.returncode,0,r.stderr)
    def test_help(self):
        for name in ('setup.sh','healthcheck.sh','monitor.sh'):
            r=run('bash',str(ROOT/name),'--help'); self.assertEqual(r.returncode,0,r.stderr)
    def test_unknown_options_rejected(self):
        for name in ('setup.sh','healthcheck.sh','monitor.sh'):
            r=run('bash',str(ROOT/name),'--nonsense');self.assertNotEqual(r.returncode,0)
    def test_public_key_and_config(self):
        c=v.validate(ROOT/'config.env',ROOT);self.assertEqual(c['ADMIN_USER'],'secureadmin')
    def test_key_matches_expected_fingerprint(self):
        import hashlib
        blob=base64.b64decode((ROOT/'keys/secureadmin.pub').read_text().split()[1])
        fp=base64.b64encode(hashlib.sha256(blob).digest()).decode().rstrip('=')
        self.assertEqual(fp,'YbkaUZmrQBVRwTKYPv4SyJUG0+YHA2jlr3dzN1aV8lU')
    def test_invalid_config_variants(self):
        original=(ROOT/'config.env').read_text()
        variants=[original.replace('"85"','"101"'),original.replace('"5"','"7"'),
            original.replace('"10.0.2.2"','"0.0.0.0/0"'),
            original.replace('"guest1"','"secureadmin"'),
            original.replace('"/srv/securebase"','"/etc"'),
            original.replace('"keys/secureadmin.pub"','"../private.pub"')]
        for text in variants:
            with self.subTest(text=text[-100:]),tempfile.TemporaryDirectory() as d:
                p=pathlib.Path(d)/'config.env';p.write_text(text)
                with self.assertRaises((ValueError,KeyError)):v.validate(p,ROOT)
    def test_bash_literal_parser(self):
        r=run('bash','-c','set -euo pipefail; source "$1/lib/common.sh"; load_config "$1/config.env"; echo "$ADMIN_USER:$SSH_PORT"','bash',str(ROOT))
        self.assertEqual(r.returncode,0,r.stderr);self.assertIn('secureadmin:22',r.stdout)
    def test_injection_not_executed(self):
        with tempfile.TemporaryDirectory() as d:
            p=pathlib.Path(d)/'bad.env';marker=pathlib.Path(d)/'pwned'
            p.write_text(f'HOSTNAME="$(touch {marker})"\n')
            r=run('bash','-c','set -euo pipefail; source "$1/lib/common.sh"; load_config "$2"','bash',str(ROOT),str(p))
            self.assertNotEqual(r.returncode,0);self.assertFalse(marker.exists())
    def test_duplicate_and_unknown_keys(self):
        for extra in ('HOSTNAME="duplicate"\n','UNRECOGNISED="x"\n'):
            with tempfile.TemporaryDirectory() as d:
                p=pathlib.Path(d)/'bad.env';p.write_text((ROOT/'config.env').read_text()+extra)
                r=run('bash','-c','set -euo pipefail; source "$1/lib/common.sh"; load_config "$2"','bash',str(ROOT),str(p))
                self.assertNotEqual(r.returncode,0)
    def test_monitor_boundaries(self):
        r=run('bash',str(ROOT/'monitor.sh'),'--self-test');self.assertEqual(r.returncode,0,r.stdout+r.stderr)
        self.assertEqual(r.stdout.count('[TEST]'),5)
    def test_monitor_sample(self):
        r=run('bash',str(ROOT/'monitor.sh'),'--sample','--config','/nonexistent/securebase-test')
        self.assertEqual(r.returncode,0,r.stderr)
        self.assertRegex(r.stdout,r'CPU=\d+\.\d% MEMORY=\d+\.\d% DISK=\d+% STATUS=')
    def test_monitor_bad_config(self):
        with tempfile.TemporaryDirectory() as d:
            p=pathlib.Path(d)/'bad.conf';p.write_text('DISK_THRESHOLD="101"\n')
            r=run('bash',str(ROOT/'monitor.sh'),'--sample','--config',str(p));self.assertNotEqual(r.returncode,0)
    def test_netplan_single_nic(self):
        self.assertTrue(n.check({'network':{'version':2,'ethernets':{'enp0s3':{'dhcp4':True}}}},'enp0s3'))
    def test_netplan_rejects_extra_interfaces_and_bridges(self):
        for data in ({'ethernets':{'enp0s3':{},'enp0s8':{}}},{'ethernets':{'enp0s3':{}},'bridges':{}}, {'renderer':'NetworkManager','ethernets':{'enp0s3':{}}}):
            with self.assertRaises(ValueError):n.check(data,'enp0s3')
    def test_ufw_rule_policy(self):
        for text,expected in [('',0),('ufw allow from 10.0.2.2 to any port 22 proto tcp',0),
            ('ufw allow proto tcp from 10.0.2.2/32 to any port 22',0),
            ('ufw allow 22/tcp',1),('ufw allow from 10.0.2.2 to any port 8080 proto tcp',1)]:
            command='set -euo pipefail; source "$1/lib/common.sh"; SSH_ALLOWED_SOURCE=10.0.2.2; SSH_PORT=22; RULE=$2; ufw() { printf "%s\\n" "$RULE"; }; check_ufw_rules'
            r=run('bash','-c',command,'bash',str(ROOT),text)
            self.assertEqual(int(r.returncode!=0),expected,r.stderr)
    @unittest.skipUnless(os.geteuid()==0,'Filmetadata-test kraever root i isoleret container')
    def test_atomic_install_idempotence_and_backup(self):
        with tempfile.TemporaryDirectory() as d:
            script=r"""set -euo pipefail
source "$1/lib/common.sh"
BACKUP_ROOT="$2/backups"
printf 'one\n' > "$2/input"
install_managed "$2/input" "$2/output" 0640
[[ $CHANGED == 1 ]]
stamp=$(stat -c %Y "$2/output")
install_managed "$2/input" "$2/output" 0640
[[ $CHANGED == 0 && $(stat -c %Y "$2/output") == "$stamp" ]]
printf 'two\n' > "$2/input"
install_managed "$2/input" "$2/output" 0640
[[ $CHANGED == 1 ]]
grep -Fxq one "$BACKUP_ROOT$2/output"
[[ $(stat -c %a "$2/output") == 640 ]]
"""
            r=run('bash','-c',script,'bash',str(ROOT),d);self.assertEqual(r.returncode,0,r.stdout+r.stderr)
    @unittest.skipUnless(os.geteuid()==0,'Kraever root i isoleret container')
    def test_symlink_target_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            p=pathlib.Path(d);(p/'source').write_text('new');(p/'victim').write_text('unchanged');(p/'dest').symlink_to(p/'victim')
            r=run('bash','-c','set -euo pipefail; source "$1/lib/common.sh"; install_managed "$2/source" "$2/dest" 0644','bash',str(ROOT),d)
            self.assertNotEqual(r.returncode,0);self.assertEqual((p/'victim').read_text(),'unchanged')
    def test_exact_sudo_policy(self):
        script=ROOT/'tools/check_sudo_listing.py'
        valid="""User secureadmin may run the following commands:
    (root) NOPASSWD: /usr/sbin/sshd -t
    (root) NOPASSWD: /usr/bin/systemctl reload ssh.service
    (root) NOPASSWD: /usr/bin/journalctl --no-pager -u ssh.service -n 30
"""
        self.assertEqual(run(sys.executable,str(script),input=valid).returncode,0)
        for extra in ('    (ALL : ALL) ALL\n','    (root) /bin/bash\n'):
            self.assertNotEqual(run(sys.executable,str(script),input=valid+extra).returncode,0)
    def test_no_private_keys(self):
        for p in ROOT.rglob('*'):
            if p.is_file() and p.suffix not in ('.pyc',):
                self.assertNotIn(b'-----BEGIN '+b'OPENSSH PRIVATE KEY-----',p.read_bytes(),str(p))
    def test_no_crlf_or_missing_final_newline(self):
        for p in list(ROOT.rglob('*.sh'))+list(ROOT.rglob('*.env'))+list(ROOT.rglob('*.pub')):
            raw=p.read_bytes();self.assertNotIn(b'\r',raw,str(p));self.assertTrue(raw.endswith(b'\n'),str(p))
if __name__=='__main__':unittest.main(verbosity=2)
