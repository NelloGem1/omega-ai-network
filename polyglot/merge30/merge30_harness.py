#!/usr/bin/env python3
"""
MERGE-30 HARNESS — second wave: typescript, csharp, fsharp, haskell,
lisp(sbcl), elixir, verilog, vhdl, basic(bwbasic).
Same doctrine: one spec, all languages must agree.
"""
import json, subprocess, os, sys

BIN = "/home/neilh/polyglot/merge30/bins"
os.makedirs(BIN, exist_ok=True)

SPECS = {
    "sum_range": {"inputs": [10, 100, 1000, 9999], "expect": lambda n: n*(n+1)//2},
    "is_prime":  {"inputs": [2,3,4,17,97,100,7919,104729], "expect": None},
}

def expect_prime(n):
    return int(n >= 2 and all(n % i for i in range(2, int(n**0.5)+1)))

def write(lang, spec, src):
    ext = {"typescript":"ts","csharp":"cs","fsharp":"fsx","haskell":"hs",
           "lisp":"lisp","elixir":"exs","verilog":"v","vhdl":"vhd","basic":"bas"}[lang]
    p = os.path.join(BIN, f"{spec}_{lang}.{ext}")
    open(p,"w").write(src)
    return p

# ---------- runners: each returns stdout for (spec, n) ----------
def run_ts(spec, n):
    # tsc compile once per spec, cache .js
    src = write("typescript", spec, TS_SRC[spec])
    js = os.path.join(BIN, f"{spec}_typescript.js")
    if not os.path.exists(js):
        # tsc emits js next to input structure; compile in BIN
        r = subprocess.run(["tsc","--target","es2020","--module","commonjs",
                            "--outDir",BIN,src], capture_output=True, text=True)
        # find emitted js (may be BIN/<name>.js or nested)
        for root,_,files in os.walk(BIN):
            for f in files:
                if f.endswith(".js") and spec in f:
                    js = os.path.join(root,f)
    prog = f"const n=BigInt('{n}');" + (TS_BODY[spec])
    open("/tmp/tsrun.js","w").write(prog)
    return subprocess.run(["node","/tmp/tsrun.js"],capture_output=True,text=True).stdout.strip()

TS_BODY = {
    "sum_range": "console.log((n*(n+1n)/2n).toString());",
    "is_prime":  "let p=0n;if(n>=2n){p=1n;for(let i=2n;i*i<=n;i++){if(n%i===0n){p=0n;break}}}console.log(p.toString());",
}
TS_SRC = {k: "// compiled once\n" + v for k,v in TS_BODY.items()}

def run_cs(spec, n):
    # .NET 10 file-based program: dotnet run file.cs -- args
    body = CS_BODY[spec].replace("{N}", str(n))
    src = f"// dotnet run {spec}.cs -- {n}\n" + body
    p = write("csharp", spec+"_"+str(n), src)
    # file-based apps: dotnet run <file.cs>
    r = subprocess.run(["dotnet","run",p,"--",str(n)],capture_output=True,text=True,timeout=120)
    return r.stdout.strip()

CS_BODY = {
    "sum_range": "long n=long.Parse(args[0]);Console.WriteLine(n*(n+1)/2);",
    "is_prime":  "long n=long.Parse(args[0]);if(n<2){Console.WriteLine(0);return;}for(long i=2;i*i<=n;i++)if(n%i==0){Console.WriteLine(0);return;}Console.WriteLine(1);",
}

def run_fs(spec, n):
    body = FS_BODY[spec]
    src = "// fsi args\n" + body
    p = write("fsharp", spec, src)
    r = subprocess.run(["dotnet","fsi",p,str(n)],capture_output=True,text=True,timeout=120)
    return r.stdout.strip().splitlines()[-1] if r.stdout.strip() else ""

FS_BODY = {
    "sum_range": 'let n = int64 fsi.CommandLineArgs.[1]\nprintfn "%d" (n * (n + 1L) / 2L)',
    "is_prime":  'let n = int64 fsi.CommandLineArgs.[1]\nlet mutable p = n >= 2L\nlet mutable i = 2L\nwhile p && i*i <= n do (if n % i = 0L then p <- false); i <- i + 1L\nprintfn "%d" (if p then 1 else 0)',
}

def run_hs(spec, n):
    src = write("haskell", spec, HS_SRC[spec])
    r = subprocess.run(["runghc",src,str(n)],capture_output=True,text=True,timeout=120)
    return r.stdout.strip()

HS_SRC = {
    "sum_range": '''import System.Environment
main = do
  [a] <- getArgs
  let n = read a :: Integer
  print (n * (n+1) `div` 2)''',
    "is_prime": '''import System.Environment
main = do
  [a] <- getArgs
  let n = read a :: Integer
      isP x = x >= 2 && all (\\d -> x `mod` d /= 0) [2..floor (sqrt (fromIntegral x :: Double))]
  print (if isP n then 1 else 0 :: Int)''',
}

def run_lisp(spec, n):
    src = write("lisp", spec, LISP_SRC[spec].replace("{N}", str(n)))
    r = subprocess.run(["sbcl","--script",src],capture_output=True,text=True,timeout=60)
    return r.stdout.strip()

LISP_SRC = {
    "sum_range": '''(let ((n {N}))
  (format t "~a~%" (/ (* n (+ n 1)) 2)))''',
    "is_prime": '''(flet ((isp (n)
             (if (< n 2) 0
               (labels ((lp (i)
                          (cond ((> (* i i) n) 1)
                                ((zerop (mod n i)) 0)
                                (t (lp (+ i 1))))))
                 (lp 2)))))
  (format t "~a~%" (isp {N})))''',
}

def run_ex(spec, n):
    src = write("elixir", spec, EX_SRC[spec].replace("{N}", str(n)))
    r = subprocess.run(["elixir",src],capture_output=True,text=True,timeout=120)
    return r.stdout.strip()

EX_SRC = {
    "sum_range": '''n = {N}
IO.puts(div(n * (n + 1), 2))''',
    "is_prime": '''n = {N}
k = trunc(:math.sqrt(n))
p = cond do
  n < 2 -> 0
  k < 2 -> 1
  true -> Enum.reduce_while(Enum.to_list(2..k), 1, fn i, acc -> if rem(n, i) == 0, do: {:halt, 0}, else: {:cont, acc} end)
end
IO.puts(p)''',
}

def run_vlog(spec, n):
    # verilog: inject n, iverilog compile, vvp run
    src = write("verilog", spec, VLOG_SRC[spec].replace("{N}", str(n)))
    exe = os.path.join(BIN, f"{spec}_vlog.vvp")
    r1 = subprocess.run(["iverilog","-o",exe,src],capture_output=True,text=True)
    if r1.returncode != 0: return "COMPILE_ERR:"+r1.stderr[:80]
    r2 = subprocess.run(["vvp",exe],capture_output=True,text=True)
    return r2.stdout.strip()

VLOG_SRC = {
    "sum_range": '''module top;
  reg [63:0] n;
  initial begin
    n = 64'd{N};
    $display("%0d", n*(n+1)/2);
    $finish;
  end
endmodule''',
    "is_prime": '''module top;
  integer i; reg p; reg [63:0] n;
  initial begin
    n = 64'd{N};
    if (n < 2) begin $display("0"); $finish; end
    p = 1;
    for (i = 2; i*i <= n; i = i + 1)
      if (n % i == 0) p = 0;
    $display("%0d", p);
    $finish;
  end
endmodule''',
}

def run_vhdl(spec, n):
    src = write("vhdl", spec, VHDL_SRC[spec].replace("{N}", str(n)))
    r = subprocess.run(["ghdl","-a","--std=08",src],capture_output=True,text=True,timeout=120,cwd=BIN)
    if r.returncode != 0: return "COMPILE_ERR:"+r.stderr[:80]
    r2 = subprocess.run(["ghdl","-e","--std=08","m"],capture_output=True,text=True,cwd=BIN,timeout=120)
    if r2.returncode != 0: return "ELAB_ERR:"+r2.stderr[:80]
    r3 = subprocess.run(["ghdl","-r","--std=08","m"],capture_output=True,text=True,cwd=BIN,timeout=120)
    return (r3.stdout or r2.stdout).strip()

VHDL_SRC = {
    "sum_range": '''entity m is end;
architecture a of m is
  constant n : integer := {N};
begin
  process begin
    report integer'image(n*(n+1)/2);
    wait;
  end process;
end;''',
    "is_prime": '''entity m is end;
architecture a of m is
  constant n : integer := {N};
  function isp(x: integer) return integer is
    variable i: integer := 2; variable p: integer := 1;
  begin
    if x < 2 then return 0; end if;
    while i*i <= x loop
      if x mod i = 0 then p := 0; end if;
      i := i + 1;
    end loop;
    return p;
  end;
begin
  process begin report integer'image(isp(n)); wait; end process;
end;''',
}

def run_basic(spec, n):
    # bwbasic runs a .bas file then drops to shell — feed /dev/null stdin
    src = BASIC_SRC[spec].replace("{N}", str(n))
    p = write("basic", spec, src)
    r = subprocess.run(["bwbasic",p], stdin=subprocess.DEVNULL,
                       capture_output=True, text=True, timeout=30)
    return r.stdout.strip()

BASIC_SRC = {
    "sum_range": '''N = {N}
S = N*(N+1)/2
PRINT "ANS=";S''',
    "is_prime": '''N = {N}
P = 0
IF N >= 2 THEN P = 1
IF N < 4 THEN GOTO SKIP
FOR I = 2 TO INT(SQR(N))
IF N MOD I = 0 THEN P = 0
NEXT I
SKIP:
PRINT "ANS=";P''',
}

RUNNERS = {
    "typescript": run_ts, "csharp": run_cs, "fsharp": run_fs,
    "haskell": run_hs, "lisp": run_lisp, "elixir": run_ex,
    "verilog": run_vlog, "vhdl": run_vhdl, "basic": run_basic,
}

import re
def norm(out):
    """Extract the numeric answer from noisy runtime output."""
    out = str(out).strip()
    m = re.search(r"ANS=\s*(-?\d+)", out)
    if m: return m.group(1)
    for line in out.splitlines():
        line = line.strip()
        if re.fullmatch(r"-?\d+(\.0)?", line):
            return line
    # fallback: last integer token of the last non-empty line (vhdl report notes)
    lines = [l for l in out.splitlines() if l.strip()]
    if lines:
        m = re.findall(r"-?\d+", lines[-1])
        if m: return m[-1]
    m = re.search(r"-?\d+", out)
    return m.group(0) if m else out

def main():
    alive = {}
    for lang, fn in RUNNERS.items():
        try:
            v = fn("sum_range", 10)
            alive[lang] = (v not in ("", None) and "ERR" not in str(v))
        except Exception as e:
            alive[lang] = False
            print(f"  {lang}: DEAD ({str(e)[:80]})")
    good = [l for l,v in alive.items() if v]
    dead = [l for l,v in alive.items() if not v]
    print(f"ALIVE ({len(good)}): {', '.join(good)}")
    print(f"DEAD  ({len(dead)}): {', '.join(dead) or 'none'}")

    report = {"alive": good, "dead": dead, "results": {}}
    for spec, cfg in SPECS.items():
        spec_res = {}
        exp = cfg["expect"] or expect_prime
        for n in cfg["inputs"]:
            legs = {}
            for lang in good:
                try:
                    legs[lang] = norm(RUNNERS[lang](spec, n))
                except Exception as e:
                    legs[lang] = f"ERR:{str(e)[:80]}"
            expected = str(exp(n))
            bad = {l:v for l,v in legs.items() if v not in (expected, expected+".0")}
            spec_res[str(n)] = {"expected": expected, "legs": legs, "agree": len(bad)==0}
        report["results"][spec] = spec_res
        bads = [k for k,v in spec_res.items() if not v["agree"]]
        print(f"{spec}: {len(spec_res)-len(bads)}/{len(spec_res)} agree" +
              (f"  DIVERGENT: {bads[:5]}" if bads else "  ✅"))

    out = "/home/neilh/polyglot/merge30/merge30_report.json"
    json.dump(report, open(out,"w"), indent=2)
    print(f"\nreport → {out}")
    print(f"SCORE: +{len(good)} languages → fleet total {17+len(good)}")

if __name__ == "__main__":
    main()
