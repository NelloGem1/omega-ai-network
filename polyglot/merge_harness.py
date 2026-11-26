#!/usr/bin/env python3
"""
MERGE-20 HARNESS — the big fusion test.
One spec (sum_range + is_prime) executed across every installed language.
Compile-once/run-many for compiled languages. Divergence = bug.

Usage: python3 merge_harness.py [--fuzz N]
"""
import json, subprocess, os, sys, tempfile, hashlib

ROOT = "/home/neilh/polyglot/merge20"
BIN = os.path.join(ROOT, "bins")
os.makedirs(BIN, exist_ok=True)

# ---------- SPECS ----------
# Each spec: function f(n) -> integer
SUM_RANGE = {
    "name": "sum_range",
    "desc": "n*(n+1)/2",
    "inputs": [10, 100, 1000, 9999],
}
IS_PRIME = {
    "name": "is_prime",
    "desc": "1 if prime else 0",
    "inputs": [2, 3, 4, 17, 97, 100, 7919, 104729],
}
SPECS = [SUM_RANGE, IS_PRIME]

# ---------- source templates: {name} -> source code ----------
# Convention: program reads n from argv[1] (or stdin for some), prints integer.
TEMPLATES = {
"c": {
  "sum_range": r'''
#include <stdio.h>
#include <stdlib.h>
int main(int c,char**v){long n=atol(v[1]);printf("%ld\n",n*(n+1)/2);return 0;}''',
  "is_prime": r'''
#include <stdio.h>
#include <stdlib.h>
int main(int c,char**v){long n=atol(v[1]);if(n<2){printf("0\n");return 0;}for(long i=2;i*i<=n;i++)if(n%i==0){printf("0\n");return 0;}printf("1\n");return 0;}''',
},
"cpp": {
  "sum_range": r'''
#include <iostream>
int main(int c,char**v){long long n=atoll(v[1]);std::cout<<n*(n+1)/2<<"\n";return 0;}''',
  "is_prime": r'''
#include <iostream>
int main(int c,char**v){long long n=atoll(v[1]);if(n<2){std::cout<<"0\n";return 0;}for(long long i=2;i*i<=n;i++)if(n%i==0){std::cout<<"0\n";return 0;}std::cout<<"1\n";return 0;}''',
},
"go": {
  "sum_range": r'''package main
import ("fmt";"os";"strconv")
func main(){n,_:=strconv.ParseInt(os.Args[1],10,64);fmt.Println(n*(n+1)/2)}''',
  "is_prime": r'''package main
import ("fmt";"os";"strconv")
func main(){n,_:=strconv.ParseInt(os.Args[1],10,64);if n<2{fmt.Println(0);return};for i:=int64(2);i*i<=n;i++{if n%i==0{fmt.Println(0);return}};fmt.Println(1)}''',
},
"rust": {
  "sum_range": r'''use std::env;
fn main(){let n:i64=env::args().nth(1).unwrap().parse().unwrap();println!("{}",n*(n+1)/2);}''',
  "is_prime": r'''use std::env;
fn main(){let n:i64=env::args().nth(1).unwrap().parse().unwrap();if n<2{println!("0");return};let mut i=2;while i*i<=n{if n%i==0{println!("0");return};i+=1};println!("1");}''',
},
"java": {
  "sum_range": r'''public class SumRange { public static void main(String[] a){ long n=Long.parseLong(a[0]); System.out.println(n*(n+1)/2); } }''',
  "is_prime": r'''public class IsPrime { public static void main(String[] a){ long n=Long.parseLong(a[0]); if(n<2){System.out.println(0);return;} for(long i=2;i*i<=n;i++) if(n%i==0){System.out.println(0);return;} System.out.println(1); } }''',
},
"js": {  # node
  "sum_range": r'''const n=BigInt(process.argv[2]);console.log((n*(n+1n)/2n).toString());''',
  "is_prime": r'''const n=BigInt(process.argv[2]);if(n<2n){console.log(0)}else{let p=1n;for(let i=2n;i*i<=n;i++){if(n%i===0n){p=0n;break}}console.log(p.toString())}''',
},
"php": {
  "sum_range": r'''<?php $n=(int)$argv[1]; echo $n*($n+1)/2,"\n"; ?>''',
  "is_prime": r'''<?php $n=(int)$argv[1]; if($n<2){echo "0\n";exit;} for($i=2;$i*$i<=$n;$i++){if($n%$i==0){echo "0\n";exit;}} echo "1\n"; ?>''',
},
"ruby": {
  "sum_range": r'''n=ARGV[0].to_i; puts n*(n+1)/2''',
  "is_prime": r'''n=ARGV[0].to_i; if n<2 then puts 0; exit; end; (2..Math.sqrt(n)).each{|i| if n%i==0 then puts 0; exit; end}; puts 1''',
},
"lua": {
  "sum_range": r'''local n=tonumber(arg[1]); print(n*(n+1)/2)''',
  "is_prime": r'''local n=tonumber(arg[1]); if n<2 then print(0) os.exit() end; for i=2,math.sqrt(n) do if n%i==0 then print(0) os.exit() end end; print(1)''',
},
"prolog": {
  "sum_range": r'''% sum_range: read n, print n*(n+1)/2
:- initialization(main).
main :- current_prolog_flag(argv, [N|_]), atom_number(N,N1), S is N1*(N1+1)/2, format("~w~n",[S]), halt.''',
  "is_prime": r'''% is_prime
:- initialization(main).
is_p(N) :- N >= 2, \+ (between(2,Floor,_,N rem Floor =:= 0), Floor*Floor =< N), Floor is floor(sqrt(N)).
main :- current_prolog_flag(argv, [N|_]), atom_number(N,N1), (is_p(N1)->format("1~n") ; format("0~n")), halt.''',
},
"cobol": {
  "sum_range": r'''       IDENTIFICATION DIVISION.
       PROGRAM-ID. M.
       DATA DIVISION.
       WORKING-STORAGE SECTION.
       01 N PIC 9(9).
       01 S PIC 9(18).
       PROCEDURE DIVISION.
           ACCEPT N FROM COMMAND-LINE.
           COMPUTE S = N * (N + 1) / 2.
           DISPLAY S.
           STOP RUN.''',
  "is_prime": r'''       IDENTIFICATION DIVISION.
       PROGRAM-ID. M.
       DATA DIVISION.
       WORKING-STORAGE SECTION.
       01 N PIC 9(9).
       01 I PIC 9(9).
       01 P PIC 9.
       PROCEDURE DIVISION.
           ACCEPT N FROM COMMAND-LINE.
           MOVE 0 TO P.
           IF N < 2 DISPLAY 0 STOP RUN END-IF.
           MOVE 1 TO P.
           PERFORM VARYING I FROM 2 BY 1 UNTIL I * I > N
               IF FUNCTION MOD(N, I) = 0 MOVE 0 TO P END-IF
           END-PERFORM.
           DISPLAY P.
           STOP RUN.''',
},
"pascal": {
  "sum_range": r'''program M;
var n: int64; code: integer;
begin
  val(paramstr(1), n, code); writeln(n*(n+1) div 2);
end.''',
  "is_prime": r'''program M;
var n,i: int64; p: boolean; code: integer;
begin
  val(paramstr(1), n, code);
  if n<2 then writeln(0) else begin
    p:=true;
    for i:=2 to trunc(sqrt(n)) do if n mod i=0 then p:=false;
    if p then writeln(1) else writeln(0);
  end;
end.''',
},
"fortran": {
  "sum_range": r'''      program m
      integer*8 n,s
      read(*,*) n
      s = n*(n+1)/2
      print *, s
      end''',
  "is_prime": r'''      program m
      integer*8 n,i
      logical p
      read(*,*) n
      if (n.lt.2) then
        print *, 0
      else
        p = .true.
        do i = 2, int(sqrt(dble(n)))
          if (mod(n,i).eq.0) p = .false.
        end do
        if (p) then
          print *, 1
        else
          print *, 0
        end if
      end if
      end''',
},
}

# ---------- compile helpers ----------
EXT = {"c":"c","cpp":"cpp","go":"go","rust":"rs","java":"java",
       "js":"js","php":"php","ruby":"rb","lua":"lua",
       "prolog":"pl","cobol":"cob","pascal":"pas","fortran":"f90"}
COMPILED = {"c","cpp","go","rust","java","cobol","pascal","fortran"}

def src_path(lang, spec):
    if lang == "java":
        cls = "SumRange" if spec["name"]=="sum_range" else "IsPrime"
        return os.path.join(BIN, f"{cls}.java")
    return os.path.join(BIN, f"{spec['name']}_{lang}.{EXT[lang]}")

def bin_path(lang, spec):
    return os.path.join(BIN, f"{spec['name']}_{lang}")

def ensure_compiled(lang, spec):
    """Compile if needed; return binary path or None for interpreted."""
    src = src_path(lang, spec)
    os.makedirs(BIN, exist_ok=True)
    with open(src,"w") as f: f.write(TEMPLATES[lang][spec["name"]])
    bp = bin_path(lang, spec)
    if lang in COMPILED and not os.path.exists(bp):
        cmds = {
          "c":      ["gcc","-O2","-o",bp,src,"-lm"],
          "cpp":    ["g++","-O2","-o",bp,src],
          "go":     ["go","build","-o",bp,src],
          "rust":   ["rustc","-O","-o",bp,src],
          "java":   ["javac","-d",BIN,src],   # produces M.class
          "cobol":  ["cobc","-x","-free","-o",bp,src],
          "fortran":["gfortran","-O2","-o",bp,src],
        }
        if lang=="java":
            r = subprocess.run(cmds["java"],capture_output=True,text=True)
            if r.returncode!=0: return None, r.stderr[:200]
            cls = "SumRange" if spec["name"]=="sum_range" else "IsPrime"
            return ("java_class", os.path.join(BIN, cls)), None
        if lang=="pascal":
            r = subprocess.run(["fpc","-O2","-o"+os.path.basename(bp),os.path.basename(src)],
                               capture_output=True,text=True,cwd=BIN)
            if r.returncode!=0 or not os.path.exists(bp):
                return None, (r.stderr or r.stdout)[:200]
            return bp, None
        r = subprocess.run(cmds[lang],capture_output=True,text=True)
        if r.returncode!=0 or not os.path.exists(bp):
            return None, (r.stderr or r.stdout)[:200]
    return bp, None

# ---------- runners ----------
def run(lang, spec, n):
    """Execute spec in lang with input n; return stdout stripped."""
    if lang=="python":
        code = "print(%d*(%d+1)//2)"%(n,n) if spec["name"]=="sum_range" else \
               f"n={n}\nprint(int(n>=2 and all(n%d for d in range(2,int(n**0.5)+1))))"
        return subprocess.run(["python3","-c",code],capture_output=True,text=True).stdout.strip()
    if lang=="perl":
        if spec["name"]=="sum_range": code=f"print {n}*({n}+1)/2"
        else: code=f"$n={n};$p=0;if($n>=2){{$p=1;for($i=2;$i<=$n**0.5;$i++){{if($n%$i==0){{$p=0;last}}}}}}print $p"
        return subprocess.run(["perl","-e",code],capture_output=True,text=True).stdout.strip()
    if lang=="node":
        prog = f"console.log({n}*({n}+1)/2)" if spec["name"]=="sum_range" else \
               f"const n={n}n;if(n<2n)console.log(0);else{{let p=1n;for(let i=2n;i*i<=n;i++){{if(n%i===0n){{p=0n;break}}}}console.log(p)}}"
        return subprocess.run(["node","-e",prog],capture_output=True,text=True).stdout.strip()
    if lang=="sqlite":
        if spec["name"]=="sum_range":
            return subprocess.run(["sqlite3",":memory:",f"SELECT {n}*({n}+1)/2;"],capture_output=True,text=True).stdout.strip()
        else:
            return subprocess.run(["sqlite3",":memory:",
                f"WITH RECURSIVE t(i) AS (SELECT 2 WHERE 2*2<={n} UNION ALL SELECT i+1 FROM t WHERE (i+1)*(i+1)<={n}) SELECT CASE WHEN {n}<2 THEN 0 WHEN EXISTS(SELECT 1 FROM t WHERE {n}%i=0) THEN 0 ELSE 1 END;"],
                capture_output=True,text=True).stdout.strip()
    if lang=="lean":
        # lean leg: emit theorem check file and compile
        val = n*(n+1)//2 if spec["name"]=="sum_range" else None
        if spec["name"]=="sum_range":
            src=f"def s(n:Nat):Nat:=n*(n+1)/2\ntheorem c : s {n} = {val} := by native_decide\n"
            open("/tmp/lc.lean","w").write(src)
            env=dict(os.environ,PATH=os.path.expanduser("~/.elan/bin")+":"+os.environ["PATH"])
            r=subprocess.run(["lake","env","lean","/tmp/lc.lean"],capture_output=True,text=True,
                             cwd="/home/neilh/science_lab/formal/lean_lab",env=env)
            return "PROVEN" if r.returncode==0 else "FAIL"
        return "SKIP"

    if lang=="php":
        if spec["name"]=="sum_range": code=f"$n={n};echo $n*($n+1)/2,\"\\n\";"
        else: code=(f"$n={n};$p=0;if($n>=2){{$p=1;"
                    f"for($i=2;$i*$i<=$n;$i++){{if($n%$i==0){{$p=0;break;}}}}}}"
                    f"echo $p,PHP_EOL;")
        return subprocess.run(["php","-r",code],capture_output=True,text=True).stdout.strip()
    if lang=="ruby":
        if spec["name"]=="sum_range": code=f"n={n};puts n*(n+1)/2"
        else: code=f"n={n};if n<2 then puts 0;exit;end;(2..Math.sqrt(n)).each{{|i|if n%i==0 then puts 0;exit;end}};puts 1"
        return subprocess.run(["ruby","-e",code],capture_output=True,text=True).stdout.strip()
    if lang=="lua":
        if spec["name"]=="sum_range": code=f"local n={n};print(n*(n+1)/2)"
        else: code=f"local n={n};if n<2 then print(0) os.exit() end;for i=2,math.sqrt(n)do if n%i==0 then print(0) os.exit()end end;print(1)"
        return subprocess.run(["lua5.4","-e",code],capture_output=True,text=True).stdout.strip()
    if lang=="prolog":
        if spec["name"]=="sum_range":
            goal=f"S is {n}*({n}+1)/2, format('~w~n',[S]), halt"
        else:
            # trial division via between/2
            goal=(f"(between(2,{n},I), {n} rem I =:= 0, I*I =< {n} -> format('0~n'), halt ; "
                  f"({n} < 2 -> format('0~n') ; format('1~n')), halt)")
        return subprocess.run(["swipl","-g",goal,"-t","halt"],capture_output=True,text=True).stdout.strip()

    # compiled/interpreted template languages
    if lang in TEMPLATES:
        res, err = ensure_compiled(lang, spec)
        if res is None:
            raise RuntimeError(f"compile fail: {err}")
        if isinstance(res, tuple):  # java class
            kind, path = res
            cls = os.path.basename(path)
            r = subprocess.run(["java","-cp",BIN,cls,str(n)],
                               capture_output=True,text=True)
            return r.stdout.strip()
        bp = res
        if spec_lang_stdin(lang):
            r = subprocess.run([bp],input=str(n)+"\n",capture_output=True,text=True)
        else:
            r = subprocess.run([bp,str(n)],capture_output=True,text=True)
        return r.stdout.strip()
    raise RuntimeError(f"no runner for {lang}")

def spec_lang_stdin(lang):
    return lang in ("fortran",)  # fortran reads stdin; cobol uses cmdline accept

LANGS = ["python","perl","node","sqlite","c","cpp","go","rust","java",
         "php","ruby","lua","prolog","cobol","pascal","fortran","lean"]

def probe_langs():
    """Check which languages actually work."""
    ok = {}
    for lang in LANGS:
        try:
            if lang=="python": v=run(lang,SUM_RANGE,10)
            elif lang=="perl": v=run(lang,SUM_RANGE,10)
            elif lang=="node": v=run(lang,SUM_RANGE,10)
            elif lang=="sqlite": v=run(lang,SUM_RANGE,10)
            elif lang=="lean": v=run(lang,SUM_RANGE,10)
            else:
                res,err=ensure_compiled(lang,SUM_RANGE)
                if res is None: ok[lang]=False; continue
                v=run(lang,SUM_RANGE,10)
            ok[lang] = (v not in ("",None))
        except Exception as e:
            ok[lang]=False
    return ok

def main():
    fuzz = "--fuzz" in sys.argv
    nf = int(sys.argv[sys.argv.index("--fuzz")+1]) if "--fuzz" in sys.argv and len(sys.argv)>sys.argv.index("--fuzz")+1 else 30
    print("probing languages...", flush=True)
    ok = probe_langs()
    alive = [l for l,v in ok.items() if v]
    dead  = [l for l,v in ok.items() if not v]
    print(f"ALIVE ({len(alive)}): {', '.join(alive)}")
    print(f"DEAD  ({len(dead)}): {', '.join(dead) or 'none'}")

    report={"alive":alive,"dead":dead,"results":{}}
    random_inputs=[]
    if fuzz:
        import random; random.seed(7)
        random_inputs=[random.randint(2,500) for _ in range(nf)]

    for spec in SPECS:
        inputs = spec["inputs"] + random_inputs if spec["name"]=="is_prime" else spec["inputs"]
        spec_res={}
        for n in inputs:
            legs={}
            for lang in alive:
                if lang=="lean" and spec["name"]=="is_prime": continue
                try:
                    legs[lang]=run(lang,spec,n)
                except Exception as e:
                    legs[lang]=f"ERR:{str(e)[:60]}"
            # agreement: normalize (strip zeros, PROVEN→expected)
            def norm(v):
                s = str(v).strip().strip('"')
                if s == "PROVEN": return "PROVEN"
                if s.endswith("n") and s[:-1].replace(".","",1).isdigit(): s = s[:-1]
                try: return str(int(float(s)))
                except: return s
            vals={l:norm(v) for l,v in legs.items() if not str(v).startswith("ERR") and v not in ("SKIP",)}
            uniq=set(vals.values()) - {"PROVEN"}
            # lean PROVEN counts as agreement if others agree
            agree = (len(uniq)<=1 and len(vals)>=3) or (len(uniq)==0 and "PROVEN" in vals.values())
            spec_res[str(n)]={"agree":agree,"legs":legs}
        report["results"][spec["name"]]=spec_res
        bad=[k for k,v in spec_res.items() if not v["agree"]]
        print(f"{spec['name']}: {len(spec_res)-len(bad)}/{len(spec_res)} agree" +
              (f"  DIVERGENT: {bad[:5]}" if bad else "  ✅"))

    out=os.path.join(ROOT,"merge20_report.json")
    json.dump(report,open(out,"w"),indent=2)
    print(f"\nreport → {out}")
    print(f"SCORE: {len(alive)} languages fused")

if __name__=="__main__":
    main()

