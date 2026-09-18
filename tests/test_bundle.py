#!/usr/bin/env python3
"""Lokale, isolerede tests. Koerer IKKE deployment mod vaertens /etc."""
import base64, importlib.util, os, pathlib, shutil, subprocess, sys, tempfile, unittest
ROOT=pathlib.Path(__file__).resolve().parents[1]
CODE=ROOT/'scripts'
CONFIG=ROOT/'config/config.env.example'


def text(path):
    return pathlib.Path(path).read_text(encoding='utf-8')


def find_bash():
    candidates=[]
    if os.name=='nt':
        for base in (os.environ.get('ProgramFiles'), os.environ.get('ProgramFiles(x86)')):
            if base:
                candidates.extend([pathlib.Path(base)/'Git/bin/bash.exe', pathlib.Path(base)/'Git/usr/bin/bash.exe'])
    found=shutil.which('bash')
    if found:
        candidates.append(pathlib.Path(found))
    seen=set()
    for candidate in candidates:
        candidate=str(candidate)
        if candidate in seen or not pathlib.Path(candidate).exists():
            continue
        seen.add(candidate)
        try:
            r=subprocess.run([candidate,'--version'],text=True,capture_output=True,timeout=5)
        except OSError:
            continue
        if r.returncode==0:
            return candidate
    return None


BASH=find_bash()
IS_POSIX_ROOT=hasattr(os,'geteuid') and os.geteuid()==0
IS_LINUX=sys.platform.startswith('linux')

spec=importlib.util.spec_from_file_location('validate',CODE/'tools/validate_config.py')
v=importlib.util.module_from_spec(spec);spec.loader.exec_module(v)
spec2=importlib.util.spec_from_file_location('scope',CODE/'tools/netplan_scope.py')
n=importlib.util.module_from_spec(spec2);spec2.loader.exec_module(n)


def run(*cmd, **kw):
    return subprocess.run(cmd, text=True, capture_output=True,timeout=15,**kw)


def shell_path(path):
    return pathlib.Path(path).resolve().as_posix()


class BundleTests(unittest.TestCase):
    @unittest.skipUnless(BASH,'Bash/Git Bash er ikke tilgaengelig paa denne vaert')
    def test_all_bash_syntax(self):
        for f in ROOT.rglob('*.sh'):
            with self.subTest(file=str(f.relative_to(ROOT))):
                r=run(BASH,'-n',shell_path(f));self.assertEqual(r.returncode,0,r.stdout+r.stderr)

    @unittest.skipUnless(BASH,'Bash/Git Bash er ikke tilgaengelig paa denne vaert')
    def test_help(self):
        for name in ('setup.sh','healthcheck.sh','monitor.sh'):
            r=run(BASH,shell_path(CODE/name),'--help'); self.assertEqual(r.returncode,0,r.stdout+r.stderr)

    @unittest.skipUnless(BASH,'Bash/Git Bash er ikke tilgaengelig paa denne vaert')
    def test_unknown_options_rejected(self):
        for name in ('setup.sh','healthcheck.sh','monitor.sh'):
            r=run(BASH,shell_path(CODE/name),'--nonsense');self.assertNotEqual(r.returncode,0)

    def test_public_key_and_config(self):
        c=v.validate(CONFIG,ROOT);self.assertEqual(c['ADMIN_USER'],'secureadmin')

    def test_key_matches_expected_fingerprint(self):
        import hashlib
        blob=base64.b64decode(text(ROOT/'keys/secureadmin.pub').split()[1])
        fp=base64.b64encode(hashlib.sha256(blob).digest()).decode().rstrip('=')
        self.assertEqual(fp,'YbkaUZmrQBVRwTKYPv4SyJUG0+YHA2jlr3dzN1aV8lU')

    def test_invalid_config_variants(self):
        original=text(CONFIG)
        variants=[original.replace('"85"','"101"'),original.replace('"5"','"7"'),
            original.replace('"10.0.2.2"','"0.0.0.0/0"'),
            original.replace('"guest1"','"secureadmin"'),
            original.replace('"/srv/securebase"','"/etc"'),
            original.replace('"keys/secureadmin.pub"','"../private.pub"')]
        for value in variants:
            with self.subTest(text=value[-100:]),tempfile.TemporaryDirectory() as d:
                p=pathlib.Path(d)/'config.env';p.write_text(value,encoding='utf-8')
                with self.assertRaises((ValueError,KeyError)):v.validate(p,ROOT)

    @unittest.skipUnless(BASH,'Bash/Git Bash er ikke tilgaengelig paa denne vaert')
    def test_bash_literal_parser(self):
        r=run(BASH,'-c','set -euo pipefail; source "$1/scripts/lib/common.sh"; load_config "$1/config/config.env.example"; echo "$ADMIN_USER:$SSH_PORT"','bash',shell_path(ROOT))
        self.assertEqual(r.returncode,0,r.stdout+r.stderr);self.assertIn('secureadmin:22',r.stdout)

    @unittest.skipUnless(BASH,'Bash/Git Bash er ikke tilgaengelig paa denne vaert')
    def test_injection_not_executed(self):
        with tempfile.TemporaryDirectory() as d:
            p=pathlib.Path(d)/'bad.env';marker=pathlib.Path(d)/'pwned'
            p.write_text(f'HOSTNAME="$(touch {marker.as_posix()})"\n',encoding='utf-8')
            r=run(BASH,'-c','set -euo pipefail; source "$1/scripts/lib/common.sh"; load_config "$2"','bash',shell_path(ROOT),shell_path(p))
            self.assertNotEqual(r.returncode,0);self.assertFalse(marker.exists())

    @unittest.skipUnless(BASH,'Bash/Git Bash er ikke tilgaengelig paa denne vaert')
    def test_duplicate_and_unknown_keys(self):
        for extra in ('HOSTNAME="duplicate"\n','UNRECOGNISED="x"\n'):
            with tempfile.TemporaryDirectory() as d:
                p=pathlib.Path(d)/'bad.env';p.write_text(text(CONFIG)+extra,encoding='utf-8')
                r=run(BASH,'-c','set -euo pipefail; source "$1/scripts/lib/common.sh"; load_config "$2"','bash',shell_path(ROOT),shell_path(p))
                self.assertNotEqual(r.returncode,0)

    @unittest.skipUnless(IS_LINUX and BASH,'Linux-runtime-test; koeres ikke som Windows-kompatibilitetstest')
    def test_monitor_boundaries(self):
        r=run(BASH,shell_path(CODE/'monitor.sh'),'--self-test');self.assertEqual(r.returncode,0,r.stdout+r.stderr)
        self.assertEqual(r.stdout.count('[TEST]'),5)

    @unittest.skipUnless(IS_LINUX and BASH,'Linux-runtime-test; koeres ikke som Windows-kompatibilitetstest')
    def test_monitor_sample(self):
        r=run(BASH,shell_path(CODE/'monitor.sh'),'--sample','--config','/nonexistent/securebase-test')
        self.assertEqual(r.returncode,0,r.stdout+r.stderr)
        self.assertRegex(r.stdout,r'CPU=\d+\.\d% MEMORY=\d+\.\d% DISK=\d+% STATUS=')

    @unittest.skipUnless(IS_LINUX and BASH,'Linux-runtime-test; koeres ikke som Windows-kompatibilitetstest')
    def test_monitor_bad_config(self):
        with tempfile.TemporaryDirectory() as d:
            p=pathlib.Path(d)/'bad.conf';p.write_text('DISK_THRESHOLD="101"\n',encoding='utf-8')
            r=run(BASH,shell_path(CODE/'monitor.sh'),'--sample','--config',shell_path(p));self.assertNotEqual(r.returncode,0)

    def test_netplan_single_nic(self):
        self.assertTrue(n.check({'network':{'version':2,'ethernets':{'enp0s3':{'dhcp4':True}}}},'enp0s3'))

    def test_netplan_rejects_extra_interfaces_and_bridges(self):
        for data in ({'ethernets':{'enp0s3':{},'enp0s8':{}}},{'ethernets':{'enp0s3':{}},'bridges':{}}, {'renderer':'NetworkManager','ethernets':{'enp0s3':{}}}):
            with self.assertRaises(ValueError):n.check(data,'enp0s3')

    @unittest.skipUnless(BASH,'Bash/Git Bash er ikke tilgaengelig paa denne vaert')
    def test_ufw_rule_policy(self):
        for value,expected in [('',0),('ufw allow from 10.0.2.2 to any port 22 proto tcp',0),
            ('ufw allow proto tcp from 10.0.2.2/32 to any port 22',0),
            ('ufw allow 22/tcp',1),('ufw allow from 10.0.2.2 to any port 8080 proto tcp',1)]:
            command='set -euo pipefail; source "$1/scripts/lib/common.sh"; SSH_ALLOWED_SOURCE=10.0.2.2; SSH_PORT=22; RULE=$2; ufw() { printf "%s\\n" "$RULE"; }; check_ufw_rules'
            r=run(BASH,'-c',command,'bash',shell_path(ROOT),value)
            self.assertEqual(int(r.returncode!=0),expected,r.stdout+r.stderr)

    @unittest.skipUnless(IS_POSIX_ROOT,'Filmetadata-test kraever root i isoleret Linux-container')
    def test_atomic_install_idempotence_and_backup(self):
        with tempfile.TemporaryDirectory() as d:
            script=r"""set -euo pipefail
source "$1/scripts/lib/common.sh"
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
            r=run(BASH,'-c',script,'bash',shell_path(ROOT),shell_path(d));self.assertEqual(r.returncode,0,r.stdout+r.stderr)

    @unittest.skipUnless(IS_POSIX_ROOT,'Kraever root i isoleret Linux-container')
    def test_symlink_target_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            p=pathlib.Path(d);(p/'source').write_text('new',encoding='utf-8');(p/'victim').write_text('unchanged',encoding='utf-8');(p/'dest').symlink_to(p/'victim')
            r=run(BASH,'-c','set -euo pipefail; source "$1/scripts/lib/common.sh"; install_managed "$2/source" "$2/dest" 0644','bash',shell_path(ROOT),shell_path(d))
            self.assertNotEqual(r.returncode,0);self.assertEqual(text(p/'victim'),'unchanged')

    def test_exact_sudo_policy(self):
        script=CODE/'tools/check_sudo_listing.py'
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


if __name__=='__main__':
    unittest.main(verbosity=2)
